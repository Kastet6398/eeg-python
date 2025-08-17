# AI Theorem Discovery (Propositional Logic)

This project implements a compact Python system that continuously discovers candidate theorems and attempts to prove or disprove them against a given set of axioms (in propositional logic). It uses:

- A simple parser for propositional formulas
- Tseitin CNF transformation
- A DPLL SAT solver (with unit propagation and pure-literal elimination)
- A loop that generates random conjectures and classifies them as PROVEN (entailed by axioms), DISPROVEN (countermodel exists), or UNKNOWN (resource limit)

## Features

- Input axioms as formulas: variables (e.g., `A`, `B`, `P1`), connectives `~`/`!`/`not`, `&`, `|`, `->`, `<->`, and parentheses
- Generates random conjectures from a set of variables
- Proof by refutation: checks if `axioms ∧ ¬conjecture` is UNSAT
- Counterexample when conjecture is not entailed
- Configurable search depth, iteration limit, and SAT limits

## Install

Python 3.9+ recommended. No external dependencies required.

```bash
python3 -V
```

## Usage

- Axioms can be passed via `--axioms` as a `;`-separated list
- Variables used to generate conjectures can be set via `--vars`
- Control the enumeration by `--max-depth`, `--limit`, and SAT limits via `--sat-node-limit`

```bash
python3 /workspace/main.py --help | cat
```

### Example 1: Modus Ponens background

Axioms: `A -> B; A`

We expect the system to eventually prove `B`.

```bash
python3 /workspace/main.py \
  --axioms "A -> B; A" \
  --vars A,B \
  --max-depth 3 \
  --limit 20 | cat
```

### Example 2: Transitivity background

Axioms: `A -> B; B -> C`

We expect the system to eventually prove `A -> C` or disprove unrelated statements.

```bash
python3 /workspace/main.py \
  --axioms "A -> B; B -> C" \
  --vars A,B,C \
  --max-depth 3 \
  --limit 30 | cat
```

### Example 3: Pure discovery with defaults

```bash
python3 /workspace/main.py --axioms "A" --limit 25 | cat
```

## Grammar

- Variables: `A`, `B`, `C`, `P1`, etc.
- Unary: `~X`, `!X`, `not X`
- Binary: `X & Y`, `X | Y`, `X -> Y`, `X <-> Y`
- Parentheses: `(X & Y) | Z`

Operator precedence (high to low): NOT, AND, OR, IMPLIES, IFF. `->` and `<->` are right-associative.

## Notes

- This system operates in propositional logic. Extending to first-order logic would require a term language, quantifiers, Skolemization, and a first-order prover or SMT backend.
- The solver returns counterexamples when a conjecture is not entailed (i.e., `axioms ∧ ¬conjecture` is satisfiable).
- You can bound search/solve with `--sat-node-limit` to keep runs responsive.
