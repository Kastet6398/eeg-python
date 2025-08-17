# AI Theorem Discovery (Propositional Logic + Integer Math)

This project implements a compact Python system that continuously discovers candidate theorems and attempts to prove or disprove them against a given set of axioms.

- Propositional mode: custom CNF + DPLL SAT solver
- Math mode: Z3 backend for integer arithmetic with universal quantifiers

## Features

- Propositional logic parser: variables, `~ ! not & | -> <->`, parentheses
- Math logic parser: integer terms `+ - *` and comparisons `=, <=, >=, <, >`, universal quantifiers `forall x,y: ...`
- Continuous conjecture generation with random search
- Proof by refutation (prop) or SMT (math). On disproofs, returns counterexamples/witnesses
- Configurable depth/limits

## Install

Python 3.9+ recommended.

```bash
python3 -V
python3 -m pip install -r /workspace/requirements.txt
```

## Usage

Common flags:
- `--mode`: `prop` (default) or `math`
- `--axioms`: `;`-separated axioms
- `--vars`: variables to use for conjecture generation
- `--max-depth`, `--limit`, `--seed`

```bash
python3 /workspace/main.py --help | cat
```

### Propositional examples

- Modus Ponens background:
```bash
python3 /workspace/main.py \
  --mode prop \
  --axioms "A -> B; A" \
  --vars A,B \
  --max-depth 3 \
  --limit 20 | cat
```

### Math mode: rediscover arithmetic

- Peano-like background (commutativity/associativity are theorems in Z3’s integer theory, but we can guide discovery):
  - Axioms can include simple universal truths or constraints; Z3 already has Presburger arithmetic, so many are provable without extra axioms.

Try discovering simple algebraic equalities/inequalities:
```bash
python3 /workspace/main.py \
  --mode math \
  --axioms "" \
  --vars x,y,z \
  --max-depth 2 \
  --limit 20 \
  --seed 1 | cat
```
You should see statements like `forall x,y: x + y == y + x` eventually PROVEN, or witness counterexamples for false ones like `forall x: x*x < x`.

Add guiding axioms (optional):
```bash
python3 /workspace/main.py \
  --mode math \
  --axioms "forall x: x + 0 = x; forall x: x * 1 = x" \
  --vars x,y \
  --max-depth 2 \
  --limit 20 | cat
```

## Notes

- Math mode presently supports universal quantification with integer arithmetic. Counterexamples are concrete integer witnesses.
- Propositional mode returns a countermodel assignment when a conjecture is not entailed.
- Extend `math_discovery` to other theories by adding sorts, functions, and translators to Z3.
