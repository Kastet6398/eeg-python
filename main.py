import argparse
import random
import time
from typing import List, Dict, Optional

from theorem_discovery.parser import parse_formula
from theorem_discovery.prover import Prover
from theorem_discovery.conjecture import generate_random_formula, formula_to_string


def parse_axioms(axioms_str: str) -> List[str]:
    parts = [p.strip() for p in axioms_str.split(';') if p.strip()]
    return parts


def main() -> None:
    parser = argparse.ArgumentParser(description="Continuous theorem discovery and (dis)proof in propositional logic")
    parser.add_argument("--axioms", type=str, required=True, help="';' separated axioms, e.g., 'A -> B; A'")
    parser.add_argument("--vars", type=str, default="A,B,C",
                        help="Comma-separated variable names to use for conjecture generation (default: A,B,C)")
    parser.add_argument("--max-depth", type=int, default=3, help="Max depth for generated formulas")
    parser.add_argument("--limit", type=int, default=0, help="Number of conjectures to try (0 = infinite)")
    parser.add_argument("--sleep", type=float, default=0.0, help="Seconds to sleep between iterations")
    parser.add_argument("--sat-node-limit", type=int, default=20000,
                        help="Max DPLL decision nodes before giving up with UNKNOWN")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    axiom_strs = parse_axioms(args.axioms)
    axiom_asts = [parse_formula(s) for s in axiom_strs]

    variable_names = [v.strip() for v in args.vars.split(',') if v.strip()]

    prover = Prover(sat_node_limit=args.sat_node_limit)

    iteration = 0
    while True:
        iteration += 1
        conjecture = generate_random_formula(variable_names, max_depth=args.max_depth)
        result = prover.prove_or_disprove(axiom_asts, conjecture)

        status = result.status
        conj_str = formula_to_string(conjecture)

        if status == "PROVEN":
            print(f"[{iteration}] PROVEN: {conj_str}")
        elif status == "DISPROVEN":
            assignment_str = ", ".join(f"{k}={str(v)}" for k, v in sorted(result.counterexample.items()))
            print(f"[{iteration}] DISPROVEN: {conj_str}  -- counterexample: {assignment_str}")
        else:
            print(f"[{iteration}] UNKNOWN: {conj_str}")

        if args.limit and iteration >= args.limit:
            break
        if args.sleep > 0:
            time.sleep(args.sleep)


if __name__ == "__main__":
    main()