import os
import json
import subprocess

bdir = os.path.dirname(os.path.abspath(__file__))
raw_dir = os.path.join(bdir, "raw")
imp_dir = os.path.join(bdir, "improved")

required_files = [
    os.path.join(bdir, "README.md"),
    os.path.join(bdir, "SUBMISSION.txt"),
    os.path.join(bdir, "improvement.patch"),
    os.path.join(bdir, "package.json"),
    os.path.join(imp_dir, "market.js"),
    os.path.join(raw_dir, "original", "market.js"),
    os.path.join(raw_dir, "original", "README.md"),
    os.path.join(raw_dir, "step1_node_market.txt"),
    os.path.join(raw_dir, "step2_dispute_snippet.txt"),
    os.path.join(raw_dir, "custom_checks_results.json"),
    os.path.join(raw_dir, "reproduction_summary.json"),
]
for rf in required_files:
    assert os.path.exists(rf) and os.path.getsize(rf) > 0, f"Missing or empty: {rf}"

p = subprocess.run(["node", os.path.join(raw_dir, "run_custom_checks.js")], cwd=raw_dir, capture_output=True, text=True, check=True)
res = json.loads(p.stdout)

orig_checks = res["original"]["checks"]
imp_checks = res["improved"]["checks"]
assert len(orig_checks) >= 2 and len(imp_checks) >= 2
assert all(not c["passed"] for c in orig_checks), "Expected original unpatched checks to expose the 3 defects"
assert all(c["passed"] for c in imp_checks), "Expected all checks to pass on improved/market.js"

p_imp = subprocess.run(["node", os.path.join(imp_dir, "market.js")], cwd=imp_dir, capture_output=True, text=True, check=True)
assert "conserved: true" in p_imp.stdout, "Expected conserved: true in improved market.js output"

with open(os.path.join(bdir, "SUBMISSION.txt"), "r", encoding="utf-8") as f:
    sub = f.read()
assert 100 <= len(sub) <= 5000, f"Invalid SUBMISSION.txt length: {len(sub)}"

print(f"ALL bnty_0490 CHECKS PASSED! SUBMISSION.txt length = {len(sub)} chars")
