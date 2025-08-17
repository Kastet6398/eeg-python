import random
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from z3 import (
	IntSort, BoolSort, IntVal, BoolVal, ArithRef, BoolRef, Const, Function,
	And, Or, Not, Implies, Xor, If, ForAll, Exists, ULE, ULT, UGE, UGT, simplify, is_true, is_false,
)


@dataclass
class GenerationConfig:
	max_term_depth: int = 3
	max_formula_depth: int = 3
	quantifier_prob: float = 0.2
	bool_connective_prob: float = 0.6
	max_vars_per_quantifier: int = 2
	max_numeric_constant: int = 3


class FormulaGenerator:
	def __init__(self, rng: random.Random, signature):
		self.rng = rng
		self.sig = signature
		self.seen: Set[str] = set()
		self.int_var_pool = ["x", "y", "z"]
		self.bool_var_pool = ["p", "q"]

	def _fresh_vars(self) -> Tuple[Dict[str, any], Dict[str, any]]:
		int_vars: Dict[str, any] = {name: Const(name, IntSort()) for name in self.int_var_pool}
		bool_vars: Dict[str, any] = {name: Const(name, BoolSort()) for name in self.bool_var_pool}
		return int_vars, bool_vars

	def _gen_int_term(self, depth: int, int_vars: Dict[str, any]) -> ArithRef:
		if depth <= 0:
			choice = self.rng.choice(["var", "const", "num"])
			if choice == "var" and int_vars:
				return self.rng.choice(list(int_vars.values()))
			if choice == "const" and self.sig.consts:
				ints = [c for c in self.sig.consts.values() if c.sort().kind() == IntSort().kind()]
				if ints:
					return self.rng.choice(ints)
			# fallback numeric
			return IntVal(self.rng.randint(-self.cfg.max_numeric_constant, self.cfg.max_numeric_constant))

		# recursive
		op = self.rng.choice(["+", "-", "*", "var", "const", "num", "func"])
		if op in {"var", "const", "num"}:
			return self._gen_int_term(0, int_vars)
		elif op in {"+", "-"}:
			left = self._gen_int_term(depth - 1, int_vars)
			right = self._gen_int_term(depth - 1, int_vars)
			return left + right if op == "+" else left - right
		elif op == "*":
			# restrict multiplication to by small constants to stay in LIA-ish region
			left = self._gen_int_term(depth - 1, int_vars)
			k = self.rng.randint(-self.cfg.max_numeric_constant, self.cfg.max_numeric_constant)
			return left * k
		else:  # func
			candidates = [f for f in self.sig.funcs.values() if f.arity() >= 1 and f.range().kind() == IntSort().kind()]
			if not candidates:
				return self._gen_int_term(depth - 1, int_vars)
			f = self.rng.choice(candidates)
			args = []
			for i in range(f.arity()):
				if f.domain(i).kind() == IntSort().kind():
					args.append(self._gen_int_term(depth - 1, int_vars))
				else:
					# fallback int var for unexpected sort
					args.append(self._gen_int_term(depth - 1, int_vars))
			return f(*args)

	def _gen_atom(self, depth: int, int_vars: Dict[str, any]) -> BoolRef:
		choice = self.rng.choice(["=", "<=", "<", ">=", ">", "pred"])
		if choice == "pred" and any(f.range().kind() == BoolSort().kind() for f in self.sig.funcs.values()):
			preds = [f for f in self.sig.funcs.values() if f.range().kind() == BoolSort().kind()]
			p = self.rng.choice(preds)
			args = []
			for i in range(p.arity()):
				if p.domain(i).kind() == IntSort().kind():
					args.append(self._gen_int_term(max(0, depth - 1), int_vars))
				else:
					args.append(self._gen_int_term(max(0, depth - 1), int_vars))
			return p(*args)
		t1 = self._gen_int_term(max(0, depth - 1), int_vars)
		t2 = self._gen_int_term(max(0, depth - 1), int_vars)
		if choice == "=":
			return t1 == t2
		if choice == "<=":
			return t1 <= t2
		if choice == "<":
			return t1 < t2
		if choice == ">=":
			return t1 >= t2
		return t1 > t2

	def _gen_formula_core(self, depth: int, int_vars: Dict[str, any]) -> BoolRef:
		if depth <= 0:
			return self._gen_atom(0, int_vars)
		choice = self.rng.random()
		if choice < self.cfg.bool_connective_prob:
			conn = self.rng.choice(["and", "or", "imp", "xor", "not", "iff"])
			if conn == "not":
				return Not(self._gen_formula_core(depth - 1, int_vars))
			left = self._gen_formula_core(depth - 1, int_vars)
			right = self._gen_formula_core(depth - 1, int_vars)
			if conn == "and":
				return And(left, right)
			if conn == "or":
				return Or(left, right)
			if conn == "imp":
				return Implies(left, right)
			if conn == "xor":
				return Xor(left, right)
			# iff
			return (left == right)
		else:
			return self._gen_atom(depth - 1, int_vars)

	def _maybe_quantify(self, formula: BoolRef, int_vars: Dict[str, any]) -> BoolRef:
		if self.rng.random() >= self.cfg.quantifier_prob:
			return formula
		# choose subset of variables actually present from pool
		vars_in_formula: List[any] = []
		for v in int_vars.values():
			if str(v) in str(formula):
				vars_in_formula.append(v)
		if not vars_in_formula:
			return formula
		n = min(len(vars_in_formula), max(1, self.cfg.max_vars_per_quantifier))
		picked = self.rng.sample(vars_in_formula, k=self.rng.randint(1, n))
		binder = self.rng.choice(["forall", "exists"]) if self.rng.random() < 0.7 else "forall"
		if binder == "forall":
			return ForAll(picked, formula)
		return Exists(picked, formula)

	def configure(self, gen_cfg: GenerationConfig):
		self.cfg = gen_cfg

	def next_formula(self) -> BoolRef:
		# Keep sampling until we get a new formula w.r.t. s-expression
		attempts = 0
		while True:
			attempts += 1
			int_vars, _ = self._fresh_vars()
			core = self._gen_formula_core(self.cfg.max_formula_depth, int_vars)
			phi = self._maybe_quantify(core, int_vars)
			phi_s = str(phi.sexpr())
			if phi_s in self.seen:
				if attempts > 1000:
					# Reset if we are stuck
					self.seen.clear()
					attempts = 0
				continue
			self.seen.add(phi_s)
			# Mild simplification to canonicalize easy tautologies
			s = simplify(phi)
			return s