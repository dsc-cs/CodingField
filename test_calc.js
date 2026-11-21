// Node smoke test for calc.js — correct expectations, run by CI.
const { evaluate } = require('./calc.js');
const assert = require('node:assert');

const cases = [
  ['2+3', 5],
  ['2+3*4', 14],        // precedence
  ['(2+3)*4', 20],      // parens
  ['2^10', 1024],       // power
  ['10%3', 1],          // modulo
  ['-3+5', 2],          // unary
  ['2^3^2', 512],       // right-associative power: 2^(3^2)=512, not (2^3)^2=64
  ['(1+2*(3-4))', -1],  // 1 + 2*(-1) = -1
];
for (const [expr, expected] of cases) {
  assert.strictEqual(evaluate(expr), expected, `${expr} -> ${evaluate(expr)} (want ${expected})`);
}

// injection / unsafe input must be rejected
for (const bad of ["__import__('os')", '1+2.__class__', 'x+1', '', '1++']) {
  assert.throws(() => evaluate(bad), `expected ${bad || '(empty)'} to be rejected`);
}

console.log(`calc.js: ${cases.length} math cases + 5 rejection cases all pass`);
