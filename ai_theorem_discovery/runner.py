import os
import csv
import time
import random
from typing import Optional
from dataclasses import dataclass
from z3 import BoolRef

from .config import load_problem_spec
from .generator import FormulaGenerator, GenerationConfig
from .prover import TheoremProver


@dataclass
class RunOptions:
	config_path: str
	output_dir: str
	timeout_ms: int = 2000
	seed: Optional[int] = None
	max_iters: Optional[int] = None
	max_formula_depth: int = 3
	max_term_depth: int = 3
	quantifier_prob: float = 0.2


class DiscoveryRunner:
	def __init__(self, opts: RunOptions):
		self.opts = opts
		self.spec = load_problem_spec(opts.config_path)
		self.rng = random.Random(opts.seed or int(time.time()))
		self.gen = FormulaGenerator(self.rng, self.spec.signature)
		self.gen.configure(GenerationConfig(
			max_term_depth=opts.max_term_depth,
			max_formula_depth=opts.max_formula_depth,
			quantifier_prob=opts.quantifier_prob,
		))
		self.prover = TheoremProver(self.spec.axioms)

		os.makedirs(opts.output_dir, exist_ok=True)
		self.theorems_dir = os.path.join(opts.output_dir, "theorems")
		self.counterexamples_dir = os.path.join(opts.output_dir, "counterexamples")
		os.makedirs(self.theorems_dir, exist_ok=True)
		os.makedirs(self.counterexamples_dir, exist_ok=True)
		self.discoveries_csv = os.path.join(opts.output_dir, "discoveries.csv")
		self._init_csv()

	def _init_csv(self):
		if not os.path.exists(self.discoveries_csv):
			with open(self.discoveries_csv, "w", newline="", encoding="utf-8") as f:
				writer = csv.writer(f)
				writer.writerow(["timestamp", "status", "elapsed_ms", "conjecture_sexpr"]) 

	def _log_discovery(self, status: str, elapsed_ms: int, phi: BoolRef):
		with open(self.discoveries_csv, "a", newline="", encoding="utf-8") as f:
			writer = csv.writer(f)
			writer.writerow([int(time.time()), status, elapsed_ms, str(phi.sexpr())])

	def _save_sexpr(self, dir_path: str, prefix: str, phi: BoolRef, ext: str = ".smt2"):
		fname = f"{prefix}_{int(time.time()*1000)}{ext}"
		path = os.path.join(dir_path, fname)
		with open(path, "w", encoding="utf-8") as f:
			f.write(f"; generated conjecture\n{str(phi.sexpr())}\n")
		return path

	def _save_model(self, dir_path: str, prefix: str, model_sexpr: str):
		fname = f"{prefix}_{int(time.time()*1000)}.smt2"
		path = os.path.join(dir_path, fname)
		with open(path, "w", encoding="utf-8") as f:
			f.write(f"; countermodel\n{model_sexpr}\n")
		return path

	def run(self):
		iters = 0
		while self.opts.max_iters is None or iters < self.opts.max_iters:
			iters += 1
			phi = self.gen.next_formula()
			res = self.prover.prove_or_disprove(phi, timeout_ms=self.opts.timeout_ms)
			self._log_discovery(res.status, res.elapsed_ms, phi)
			if res.status == "PROVEN":
				self._save_sexpr(self.theorems_dir, "theorem", phi)
			elif res.status == "DISPROVEN" and res.model_sexpr:
				self._save_sexpr(self.counterexamples_dir, "conjecture", phi)
				self._save_model(self.counterexamples_dir, "model", res.model_sexpr)