import argparse
import random
import time
from typing import List, Dict, Optional

from theorem_discovery.parser import parse_formula
from theorem_discovery.prover import Prover
from theorem_discovery.conjecture import generate_random_formula, formula_to_string

from math_discovery.parser import parse_math_formula
from math_discovery.generator import generate_random_conjecture as gen_math_conj
from math_discovery.prover import parse_axioms as parse_math_axioms
from math_discovery.z3_backend import MathProver


def parse_axioms(axioms_str: str) -> List[str]:
    parts = [p.strip() for p in axioms_str.split(';') if p.strip()]
    return parts


def main() -> None:
    parser = argparse.ArgumentParser(description="Continuous theorem discovery and (dis)proof in propositional logic or integer arithmetic")
    parser.add_argument("--mode", choices=["prop", "math"], default="prop", help="Discovery mode: propositional (prop) or integer math (math)")
    parser.add_argument("--axioms", type=str, required=True, help="';' separated axioms")
    parser.add_argument("--vars", type=str, default="A,B,C",
                        help="Comma-separated variables (prop mode: A,B,C; math mode: x,y,z)")
    parser.add_argument("--max-depth", type=int, default=3, help="Max depth for generated formulas/terms")
    parser.add_argument("--limit", type=int, default=0, help="Number of conjectures to try (0 = infinite)")
    parser.add_argument("--sleep", type=float, default=0.0, help="Seconds to sleep between iterations")
    parser.add_argument("--sat-node-limit", type=int, default=20000,
                        help="(prop) Max DPLL decision nodes before giving up with UNKNOWN")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    variable_names = [v.strip() for v in args.vars.split(',') if v.strip()]

    if args.mode == "prop":
        axiom_strs = parse_axioms(args.axioms)
        axiom_asts = [parse_formula(s) for s in axiom_strs]
        prover = Prover(sat_node_limit=args.sat_node_limit)
    else:
        math_axioms = parse_math_axioms(args.axioms)
        mprover = MathProver()

    iteration = 0
    while True:
        iteration += 1
        if args.mode == "prop":
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
        else:
            conjecture = gen_math_conj(variable_names, max_depth=args.max_depth)
            result = mprover.prove_or_disprove(math_axioms, conjecture)
            # build a simple string for math formulas (rough)
            conj_str = str(conjecture)
            if result.status == "PROVEN":
                print(f"[{iteration}] PROVEN: {conj_str}")
            elif result.status == "DISPROVEN":
                assignment_str = ", ".join(f"{k}={v}" for k, v in sorted(result.counterexample.items()))
                print(f"[{iteration}] DISPROVEN: {conj_str}  -- witness: {assignment_str}")
            else:
                print(f"[{iteration}] UNKNOWN: {conj_str}")

        if args.limit and iteration >= args.limit:
            break
        if args.sleep > 0:
            time.sleep(args.sleep)


if __name__ == "__main__":
    main()