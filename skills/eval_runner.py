#!/usr/bin/env python3
"""
Eval Runner Framework for CodeBuddy Skills

This script provides a framework for running evals against skills:
1. Generate eval_metadata.json from evals.json
2. Grade existing outputs against assertions
3. Aggregate results into benchmark.json
4. Track what's missing and needs to be run

Usage:
    python eval_runner.py <skill_name> <iteration> [options]

Examples:
    python eval_runner.py sync-req 2 --setup          # Setup eval directories
    python eval_runner.py sync-req 2 --grade          # Grade existing outputs
    python eval_runner.py sync-req 2 --aggregate      # Aggregate results
    python eval_runner.py sync-req 2 --status         # Show completion status
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class EvalResult:
    """Result of a single eval run."""
    eval_id: int
    eval_name: str
    configuration: str
    passed: int
    failed: int
    total: int
    pass_rate: float
    time_seconds: float = 0.0
    tokens: int = 0
    expectations: Optional[List[Dict]] = None


class EvalRunner:
    """Framework for running and managing skill evals."""

    def __init__(self, skill_name: str, iteration: int, workspace_base: Optional[str] = None):
        self.skill_name = skill_name
        self.iteration = iteration

        # Determine workspace paths
        if workspace_base:
            self.workspace = Path(workspace_base)
        else:
            # Default workspace location: skills/<skill>/<skill>-workspace/iteration-N/
            script_dir = Path(__file__).parent
            self.workspace = script_dir / skill_name / f"{skill_name}-workspace" / f"iteration-{iteration}"

        self.skills_dir = Path(__file__).parent
        self.evals_config = self.skills_dir / skill_name / "evals.json"

    def load_evals_config(self) -> Dict:
        """Load the main evals.json configuration."""
        if self.evals_config.exists():
            with open(self.evals_config) as f:
                return json.load(f)
        return {"skill_name": self.skill_name, "evals": []}

    def get_eval_ids(self) -> List[int]:
        """Get list of eval IDs from configuration."""
        config = self.load_evals_config()
        return [e["id"] for e in config.get("evals", [])]

    def setup_eval_directories(self, eval_ids: Optional[List[int]] = None, configs: Optional[List[str]] = None):
        """
        Setup directory structure for evals.

        Creates:
        - iteration-N/eval-X/eval_metadata.json
        - iteration-N/eval-X/with_skill/outputs/
        - iteration-N/eval-X/without_skill/outputs/
        """
        if eval_ids is None:
            eval_ids = self.get_eval_ids()
        if configs is None:
            configs = ["with_skill", "without_skill"]

        config = self.load_evals_config()
        evals_by_id = {e["id"]: e for e in config.get("evals", [])}

        self.workspace.mkdir(parents=True, exist_ok=True)

        for eval_id in eval_ids:
            eval_dir = self.workspace / f"eval-{eval_id}"
            eval_dir.mkdir(exist_ok=True)

            # Create eval_metadata.json
            if eval_id in evals_by_id:
                eval_def = evals_by_id[eval_id]
                metadata = {
                    "eval_id": eval_id,
                    "eval_name": f"eval-{eval_id}",
                    "prompt": eval_def.get("prompt", ""),
                    "assertions": [
                        {"name": a, "check_type": "contains_keyword", "target": a}
                        for a in eval_def.get("assertions", [])
                    ] if eval_def.get("assertions") else []
                }

                # Handle assertions that are already objects
                if eval_def.get("assertions") and isinstance(eval_def["assertions"][0], dict):
                    metadata["assertions"] = eval_def["assertions"]

                metadata_path = eval_dir / "eval_metadata.json"
                if not metadata_path.exists():
                    with open(metadata_path, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    print(f"Created: {metadata_path}")

            # Create config directories
            for config_name in configs:
                config_dir = eval_dir / config_name / "outputs"
                config_dir.mkdir(parents=True, exist_ok=True)

        print(f"\nSetup complete for {len(eval_ids)} evals in {self.workspace}")

    def grade_assertion(self, output_text: str, assertion: Dict) -> Dict:
        """Grade a single assertion against output."""
        name = assertion.get('name', assertion.get('text', ''))
        check_type = assertion.get('check_type', 'contains_keyword')
        target = assertion.get('target', assertion.get('text', ''))

        passed = False
        evidence = ""

        if check_type == 'contains_keyword':
            if target in output_text:
                passed = True
                evidence = f"Found '{target}' in output"
            else:
                evidence = f"'{target}' not found in output"

        elif check_type == 'contains_multiple_keywords':
            if isinstance(target, list):
                found_all = all(kw in output_text for kw in target)
                if found_all:
                    passed = True
                    evidence = f"Found all keywords: {', '.join(target)}"
                else:
                    found = [kw for kw in target if kw in output_text]
                    missing = [kw for kw in target if kw not in output_text]
                    evidence = f"Found: {found}, Missing: {missing}"

        return {
            "text": name,
            "passed": passed,
            "evidence": evidence
        }

    def grade_run(self, eval_dir: Path, config: str) -> Optional[EvalResult]:
        """Grade a single run (with_skill or without_skill)."""
        run_dir = eval_dir / config
        outputs_dir = run_dir / "outputs"

        if not outputs_dir.exists():
            return None

        # Load eval metadata
        metadata_path = eval_dir / "eval_metadata.json"
        if not metadata_path.exists():
            return None

        with open(metadata_path) as f:
            metadata = json.load(f)

        # Read all output files
        output_text = ""
        output_files = list(outputs_dir.glob("*"))
        if not output_files:
            return None

        for output_file in output_files:
            if output_file.is_file() and output_file.suffix in ['.txt', '.md', '.json', '.csv', '.log']:
                try:
                    output_text += output_file.read_text() + "\n"
                except Exception:
                    pass

        if not output_text.strip():
            return None

        # Grade each assertion
        assertions = metadata.get('assertions', [])
        expectations = []
        for assertion in assertions:
            assertion_result = self.grade_assertion(output_text, assertion)
            expectations.append(assertion_result)

        passed = sum(1 for e in expectations if e["passed"])
        total = len(expectations)
        pass_rate = passed / total if total > 0 else 0.0

        # Load timing if available
        timing_path = run_dir / "timing.json"
        time_seconds = 0.0
        tokens = 0
        if timing_path.exists():
            with open(timing_path) as f:
                timing = json.load(f)
                time_seconds = timing.get("total_duration_seconds", 0)
                tokens = timing.get("total_tokens", 0)

        result = EvalResult(
            eval_id=metadata.get("eval_id", 0),
            eval_name=metadata.get("eval_name", f"eval-{metadata.get('eval_id', 0)}"),
            configuration=config,
            passed=passed,
            failed=total - passed,
            total=total,
            pass_rate=pass_rate,
            time_seconds=time_seconds,
            tokens=tokens,
            expectations=expectations
        )

        # Save grading.json
        grading_path = run_dir / "grading.json"
        with open(grading_path, 'w') as f:
            json.dump({
                "eval_id": result.eval_id,
                "configuration": config,
                "eval_name": result.eval_name,
                "expectations": expectations,
                "summary": {
                    "passed": result.passed,
                    "failed": result.failed,
                    "total": result.total,
                    "pass_rate": result.pass_rate
                }
            }, f, indent=2)

        return result

    def grade_all(self, eval_ids: Optional[List[int]] = None, configs: Optional[List[str]] = None) -> List[EvalResult]:
        """Grade all evals for the given configurations."""
        if eval_ids is None:
            # Find all eval directories
            eval_dirs = sorted(self.workspace.glob("eval-*"))
            eval_ids = [int(d.name.split("-")[1]) for d in eval_dirs]
        if configs is None:
            configs = ["with_skill", "without_skill"]

        results = []
        for eval_id in eval_ids:
            eval_dir = self.workspace / f"eval-{eval_id}"
            if not eval_dir.exists():
                continue

            for config in configs:
                result = self.grade_run(eval_dir, config)
                if result:
                    results.append(result)
                    status = "✓" if result.pass_rate >= 0.8 else "✗"
                    print(f"{status} eval-{eval_id} ({config}): {result.pass_rate:.0%} ({result.passed}/{result.total})")
                else:
                    print(f"✗ eval-{eval_id} ({config}): No outputs found")

        return results

    def aggregate_results(self, results: Optional[List[EvalResult]] = None) -> Dict:
        """Aggregate grading results into benchmark.json."""
        if results is None:
            results = self.grade_all()

        if not results:
            return {}

        # Group by configuration
        by_config: Dict[str, List[EvalResult]] = {"with_skill": [], "without_skill": []}
        for r in results:
            if r.configuration in by_config:
                by_config[r.configuration].append(r)

        benchmark: Dict[str, Any] = {
            "metadata": {
                "skill_name": self.skill_name,
                "skill_path": f"skills/{self.skill_name}",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "iteration": self.iteration,
                "evals_run": sorted(list(set(r.eval_id for r in results))),
                "runs_per_configuration": 1
            },
            "runs": []
        }

        # Build runs data
        for config, config_results in by_config.items():
            if not config_results:
                continue

            config_data: Dict[str, Any] = {
                "configuration": config,
                "pass_rate": sum(r.pass_rate for r in config_results) / len(config_results) * 100,
                "total_passed": sum(r.passed for r in config_results),
                "total_assertions": sum(r.total for r in config_results),
                "evals": []
            }

            for r in sorted(config_results, key=lambda x: x.eval_id):
                config_data["evals"].append({
                    "eval_id": r.eval_id,
                    "eval_name": r.eval_name,
                    "passed": r.passed,
                    "total": r.total,
                    "pass_rate": r.pass_rate * 100
                })

            benchmark["runs"].append(config_data)

        # Calculate delta if both configs present
        if len(benchmark["runs"]) == 2:
            ws = benchmark["runs"][0]["pass_rate"]
            wo = benchmark["runs"][1]["pass_rate"]
            benchmark["run_summary"] = {
                "delta": {
                    "pass_rate": f"+{ws - wo:.1f}" if ws > wo else f"{ws - wo:.1f}"
                }
            }

        # Save benchmark.json
        benchmark_path = self.workspace / "benchmark.json"
        with open(benchmark_path, 'w') as f:
            json.dump(benchmark, f, indent=2)

        print(f"\nBenchmark saved to: {benchmark_path}")
        return benchmark

    def get_status(self) -> Dict:
        """Get completion status for all evals."""
        eval_ids = self.get_eval_ids()
        configs = ["with_skill", "without_skill"]

        status: Dict[str, Any] = {
            "skill": self.skill_name,
            "iteration": self.iteration,
            "workspace": str(self.workspace),
            "total_evals": len(eval_ids),
            "evals": {}
        }

        for eval_id in eval_ids:
            eval_dir = self.workspace / f"eval-{eval_id}"
            eval_status: Dict[str, Any] = {
                "exists": eval_dir.exists(),
                "has_metadata": (eval_dir / "eval_metadata.json").exists(),
                "configs": {}
            }

            for config in configs:
                config_dir = eval_dir / config
                has_outputs = (config_dir / "outputs").exists() and any((config_dir / "outputs").glob("*"))
                has_grading = (config_dir / "grading.json").exists()

                eval_status["configs"][config] = {
                    "has_outputs": has_outputs,
                    "has_grading": has_grading,
                    "complete": has_outputs and has_grading
                }

            status["evals"][f"eval-{eval_id}"] = eval_status

        # Summary
        complete_count = sum(
            1 for e in status["evals"].values()
            if all(c["complete"] for c in e["configs"].values())
        )
        status["complete_count"] = complete_count
        status["missing_evals"] = [
            name for name, e in status["evals"].items()
            if not all(c["complete"] for c in e["configs"].values())
        ]

        return status

    def print_status(self):
        """Print a formatted status report."""
        status = self.get_status()

        print(f"\n{'='*60}")
        print(f"Eval Status: {status['skill']} iteration-{status['iteration']}")
        print(f"{'='*60}")
        print(f"Workspace: {status['workspace']}")
        print(f"Total evals: {status['total_evals']}")
        print(f"Complete: {status['complete_count']}/{status['total_evals']}")
        print()

        for eval_name, eval_status in sorted(status["evals"].items()):
            configs = eval_status["configs"]
            ws = configs["with_skill"]
            wo = configs["without_skill"]

            ws_icon = "✓" if ws["complete"] else "✗"
            wo_icon = "✓" if wo["complete"] else "✗"

            print(f"{eval_name}: with_skill={ws_icon}  without_skill={wo_icon}")

        if status["missing_evals"]:
            print(f"\nMissing: {', '.join(status['missing_evals'])}")
        else:
            print("\nAll evals complete!")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    skill_name = sys.argv[1]
    iteration = int(sys.argv[2])

    runner = EvalRunner(skill_name, iteration)

    # Parse options
    args = sys.argv[3:] if len(sys.argv) > 3 else ["--status"]

    if "--setup" in args:
        runner.setup_eval_directories()

    if "--grade" in args:
        results = runner.grade_all()
        print(f"\nGraded {len(results)} eval runs")

    if "--aggregate" in args:
        runner.aggregate_results()

    if "--status" in args or not any(a in args for a in ["--setup", "--grade", "--aggregate"]):
        runner.print_status()


if __name__ == "__main__":
    main()
