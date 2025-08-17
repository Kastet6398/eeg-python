# eeg-python

## AI Theorem Discovery (Z3-based)

A Python tool that continuously discovers conjectures from a provided logical signature and axioms, then attempts to prove or disprove them using the Z3 solver.

### Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Example

```bash
python -m ai_theorem_discovery run --config /workspace/examples/int_arith.yml --output-dir /workspace/output --timeout-ms 2000 --max-iters 50 --seed 42
```

To check a specific conjecture (in SMT-LIB2 format):

```bash
python -m ai_theorem_discovery prove --config /workspace/examples/int_arith.yml --conjecture "(forall ((x Int)) (<= x (f x)))" --timeout-ms 2000
```

### Config format (YAML)

- **sorts**: Currently supports builtin `Int` and `Bool` (more can be added).
- **constants**: Map of name to sort.
- **functions**: Map of name to `{domain: [...], range: ...}`.
- **predicates**: Same as functions but range must be `Bool`.
- **axioms_smt2**: List of SMT-LIB2 formulas (you can include either bare formulas or `(assert ...)` clauses). Quantifiers are supported.

See `examples/int_arith.yml` for a working example.

### Output

- `discoveries.csv`: Log of found conjectures with status `PROVEN | DISPROVEN | UNKNOWN` and timing.
- `theorems/`: Directory containing SMT2 files for proven conjectures.
- `counterexamples/`: Directory containing SMT2 model dumps for disproven conjectures.

### Notes

- This is a heuristic generative search. It randomly generates candidate formulas up to a size/depth limit and uses Z3 to check them against the axioms.
- You can adjust `--timeout-ms`, `--max-iters`, and `--seed` for different search behavior.