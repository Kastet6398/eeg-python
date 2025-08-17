import yaml
from typing import Dict, Any, Tuple, List
from dataclasses import dataclass
from z3 import IntSort, BoolSort, Const, Function, BoolRef, parse_smt2_string, Z3Exception


@dataclass
class Signature:
	int_sort: Any
	bool_sort: Any
	consts: Dict[str, Any]
	funcs: Dict[str, Any]
	decls: Dict[str, Any]


@dataclass
class ProblemSpec:
	signature: Signature
	axioms: List[BoolRef]


class ConfigError(Exception):
	pass


def _z3_sort_from_name(name: str):
	if name == "Int":
		return IntSort()
	if name == "Bool":
		return BoolSort()
	raise ConfigError(f"Unsupported sort: {name}")


def build_signature(cfg: Dict[str, Any]) -> Signature:
	consts: Dict[str, Any] = {}
	funcs: Dict[str, Any] = {}
	decls: Dict[str, Any] = {}

	int_sort = IntSort()
	bool_sort = BoolSort()

	constants_cfg = cfg.get("constants", {}) or {}
	for name, sort_name in constants_cfg.items():
		srt = _z3_sort_from_name(sort_name)
		c = Const(name, srt)
		consts[name] = c
		decls[name] = c

	functions_cfg = cfg.get("functions", {}) or {}
	for name, fdef in functions_cfg.items():
		domain_names = fdef.get("domain", [])
		range_name = fdef.get("range")
		if range_name is None:
			raise ConfigError(f"Function {name} missing range")
		domain_sorts = [_z3_sort_from_name(d) for d in domain_names]
		range_sort = _z3_sort_from_name(range_name)
		fd = Function(name, *domain_sorts, range_sort)
		funcs[name] = fd
		decls[name] = fd

	predicates_cfg = cfg.get("predicates", {}) or {}
	for name, pdef in predicates_cfg.items():
		domain_names = pdef.get("domain", [])
		domain_sorts = [_z3_sort_from_name(d) for d in domain_names]
		fd = Function(name, *domain_sorts, BoolSort())
		funcs[name] = fd
		decls[name] = fd

	return Signature(
		int_sort=int_sort,
		bool_sort=bool_sort,
		consts=consts,
		funcs=funcs,
		decls=decls,
	)


def parse_axioms_smt2(axioms_smt2: List[str], decls: Dict[str, Any]) -> List[BoolRef]:
	parsed: List[BoolRef] = []
	for ax in axioms_smt2:
		text = ax.strip()
		try:
			# Accept either bare formula or (assert ...) forms.
			if text.startswith("(assert"):
				nodes = parse_smt2_string(text, decls=decls)
				for n in nodes:
					parsed.append(n)
			else:
				nodes = parse_smt2_string(f"(assert {text})", decls=decls)
				for n in nodes:
					parsed.append(n)
		except Z3Exception as e:
			raise ConfigError(f"Failed to parse axiom: {text}\n{e}")
	return parsed


def load_problem_spec(config_path: str) -> ProblemSpec:
	with open(config_path, "r", encoding="utf-8") as f:
		cfg = yaml.safe_load(f)

	signature = build_signature(cfg)
	axioms_smt2 = cfg.get("axioms_smt2", []) or []
	axioms = parse_axioms_smt2(axioms_smt2, signature.decls) if axioms_smt2 else []

	return ProblemSpec(signature=signature, axioms=axioms)