import argparse
from z3 import parse_smt2_string

from .runner import DiscoveryRunner, RunOptions
from .config import load_problem_spec
from .prover import TheoremProver


def _cmd_run(args: argparse.Namespace):
	opts = RunOptions(
		config_path=args.config,
		output_dir=args.output_dir,
		timeout_ms=args.timeout_ms,
		seed=args.seed,
		max_iters=args.max_iters,
		max_formula_depth=args.max_formula_depth,
		max_term_depth=args.max_term_depth,
		quantifier_prob=args.quantifier_prob,
	)
	runner = DiscoveryRunner(opts)
	runner.run()


def _cmd_prove(args: argparse.Namespace):
	spec = load_problem_spec(args.config)
	decls = spec.signature.decls
	# Accept either bare formula or (assert ...)
	if args.conjecture.strip().startswith("(assert"):
		nodes = parse_smt2_string(args.conjecture, decls=decls)
		if not nodes:
			raise SystemExit("Failed to parse conjecture")
		phi = nodes[0]
	else:
		nodes = parse_smt2_string(f"(assert {args.conjecture})", decls=decls)
		if not nodes:
			raise SystemExit("Failed to parse conjecture")
		phi = nodes[0]
	prover = TheoremProver(spec.axioms)
	res = prover.prove_or_disprove(phi, timeout_ms=args.timeout_ms)
	print(f"status={res.status} elapsed_ms={res.elapsed_ms}")
	if res.model_sexpr:
		print(res.model_sexpr)


def main():
	parser = argparse.ArgumentParser(prog="ai_theorem_discovery")
	sub = parser.add_subparsers(dest="cmd", required=True)

	p_run = sub.add_parser("run", help="Run continuous discovery loop")
	p_run.add_argument("--config", required=True, help="Path to YAML config")
	p_run.add_argument("--output-dir", required=True, help="Output directory")
	p_run.add_argument("--timeout-ms", type=int, default=2000)
	p_run.add_argument("--seed", type=int, default=None)
	p_run.add_argument("--max-iters", type=int, default=None)
	p_run.add_argument("--max-formula-depth", type=int, default=3)
	p_run.add_argument("--max-term-depth", type=int, default=3)
	p_run.add_argument("--quantifier-prob", type=float, default=0.2)
	p_run.set_defaults(func=_cmd_run)

	p_prove = sub.add_parser("prove", help="Prove or disprove a single conjecture")
	p_prove.add_argument("--config", required=True, help="Path to YAML config")
	p_prove.add_argument("--conjecture", required=True, help="Conjecture in SMT-LIB2 syntax")
	p_prove.add_argument("--timeout-ms", type=int, default=2000)
	p_prove.set_defaults(func=_cmd_prove)

	args = parser.parse_args()
	args.func(args)


if __name__ == "__main__":
	main()