// Safe recursive-descent evaluator for the CodingField calculator.
// Mirrors calc.py: only + - * / % ^ ( ) and unary minus, no eval() / Function().
// Expression string is built from button presses; evaluate() returns a Number.

const OPS = { "+": (a,b)=>a+b, "-": (a,b)=>a-b, "*": (a,b)=>a*b, "/": (a,b)=>a/b, "%": (a,b)=>a%b, "^": (a,b)=>Math.pow(a,b) };

function tokenize(s) {
  const tokens = [];
  let i = 0;
  while (i < s.length) {
    const c = s[i];
    if (c === " ") { i++; continue; }
    if (/[0-9.]/.test(c)) {
      let num = c;
      i++;
      while (i < s.length && /[0-9.]/.test(s[i])) { num += s[i]; i++; }
      tokens.push({ type: "num", value: parseFloat(num) });
    } else if (c in OPS || c === "(" || c === ")") {
      tokens.push({ type: "op", value: c });
      i++;
    } else {
      throw new Error("unexpected character: " + c);
    }
  }
  return tokens;
}

// Grammar (precedence low -> high):
//   expr  = term (('+'|'-') term)*
//   term  = power (('*'|'/'|'%') power)*
//   power = unary ('^' power)?        // right-associative, above * /
//   unary = ('+'|'-') unary | primary
//   primary = num | '(' expr ')'

class Parser {
  constructor(tokens) { this.tokens = tokens; this.pos = 0; }
  peek() { return this.tokens[this.pos]; }
  next() { return this.tokens[this.pos++]; }
  expect(val) {
    const t = this.next();
    if (!t || t.value !== val) throw new Error("expected " + val);
    return t;
  }
  parse() {
    const v = this.expr();
    if (this.pos < this.tokens.length) throw new Error("unexpected token: " + this.tokens[this.pos].value);
    return v;
  }
  expr() {
    let left = this.term();
    while (this.peek() && this.peek().value === "+" || this.peek() && this.peek().value === "-") {
      const op = this.next().value;
      left = OPS[op](left, this.term());
    }
    return left;
  }
  term() {
    let left = this.power();
    while (this.peek() && (this.peek().value === "*" || this.peek().value === "/" || this.peek().value === "%")) {
      const op = this.next().value;
      left = OPS[op](left, this.power());
    }
    return left;
  }
  power() {
    const base = this.unary();
    if (this.peek() && this.peek().value === "^") {
      this.next();
      const exp = this.power(); // right-associative
      return Math.pow(base, exp);
    }
    return base;
  }
  unary() {
    const t = this.peek();
    if (t && t.value === "-") { this.next(); return -this.unary(); }
    if (t && t.value === "+") { this.next(); return this.unary(); }
    return this.primary();
  }
  primary() {
    const t = this.next();
    if (!t) throw new Error("unexpected end of input");
    if (t.type === "num") return t.value;
    if (t.value === "(") {
      const v = this.expr();
      this.expect(")");
      return v;
    }
    throw new Error("unexpected token: " + t.value);
  }
}

function evaluate(expr) {
  const tokens = tokenize(expr);
  if (tokens.length === 0) throw new Error("empty expression");
  const result = new Parser(tokens).parse();
  if (typeof result !== "number" || !isFinite(result)) throw new Error("invalid result");
  return result;
}

if (typeof module !== "undefined") module.exports = { evaluate, tokenize, Parser };
