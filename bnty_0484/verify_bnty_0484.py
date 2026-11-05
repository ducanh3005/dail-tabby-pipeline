import os
import json
import subprocess

bdir = os.path.dirname(os.path.abspath(__file__))
raw_dir = os.path.join(bdir, "raw")
imp_dir = os.path.join(bdir, "improved")

for rf in [
    os.path.join(bdir, "README.md"),
    os.path.join(bdir, "SUBMISSION.txt"),
    os.path.join(bdir, "improvement.patch"),
    os.path.join(imp_dir, "src", "engine.mjs"),
    os.path.join(raw_dir, "step1_npm_test.txt"),
    os.path.join(raw_dir, "step2_node_demo.txt"),
    os.path.join(raw_dir, "step3_verify_sh.txt"),
    os.path.join(raw_dir, "custom_checks_results.json"),
    os.path.join(raw_dir, "run_custom_checks.mjs"),
]:
    assert os.path.exists(rf) and os.path.getsize(rf) > 0, f"Missing: {rf}"

p = subprocess.run(["node", "run_custom_checks.mjs"], cwd=raw_dir, capture_output=True, text=True, check=True)
res = json.loads(p.stdout)
assert all(not c["passed"] for c in res["original"]["checks"]), "Original checks should fail"
assert all(c["passed"] for c in res["improved"]["checks"]), "Improved checks should pass"

subprocess.run(["node", "--test", "test/engine.test.mjs"], cwd=imp_dir, capture_output=True, text=True, check=True)

with open(os.path.join(bdir, "SUBMISSION.txt"), "r", encoding="utf-8") as f:
    sub = f.read()
assert 100 <= len(sub) <= 5000, f"Bad submission len: {len(sub)}"
print(f"ALL bnty_0484 CHECKS PASSED! SUBMISSION.txt length = {len(sub)} chars")
