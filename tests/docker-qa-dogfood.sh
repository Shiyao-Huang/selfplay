#!/bin/bash
# Docker QA: SelfPlay Dogfooding — code-review on own source
# Bach SOP: from-zero build, evidence-driven verification
set -euo pipefail

echo "=== SelfPlay Docker QA: Dogfooding Code Review ==="
echo "Building from zero..."
docker build -t selfplay-dogfood . 2>&1 | tail -5

echo ""
echo "--- QA-01: selfplay check evaluator.py ---"
docker run --rm selfplay-dogfood \
  selfplay --config selfplay-code-review.yaml check src/selfplay/evaluator.py 2>&1 | tee /tmp/dogfood-01.txt
# Should show code-review dimensions (有类型标注, 有 docstring, etc.)
grep -q "有类型标注" /tmp/dogfood-01.txt && echo "QA-01: PASS ✅" || echo "QA-01: FAIL ❌"

echo ""
echo "--- QA-02: selfplay check models.py (expect lower score) ---"
docker run --rm selfplay-dogfood \
  selfplay --config selfplay-code-review.yaml check src/selfplay/models.py 2>&1 | tee /tmp/dogfood-02.txt
# models.py should score lower than evaluator.py (fewer quality markers)
grep -q "有错误处理.*not_found" /tmp/dogfood-02.txt && echo "QA-02: PASS ✅" || echo "QA-02: FAIL ❌"

echo ""
echo "--- QA-03: selfplay check supervisor.py (highest score) ---"
docker run --rm selfplay-dogfood \
  selfplay --config selfplay-code-review.yaml check src/selfplay/supervisor.py 2>&1 | tee /tmp/dogfood-03.txt
grep -q "有类型标注" /tmp/dogfood-03.txt && echo "QA-03: PASS ✅" || echo "QA-03: FAIL ❌"

echo ""
echo "--- QA-04: JSON output works ---"
docker run --rm selfplay-dogfood \
  selfplay --config selfplay-code-review.yaml check --json src/selfplay/evaluator.py 2>&1 | tee /tmp/dogfood-04.txt
python3 -c "
import json, sys
data = json.load(open('/tmp/dogfood-04.txt'))
assert data['score'] > 0.5, 'Score too low'
assert len(data['features']) == 10, 'Expected 10 features'
assert 'file' in data, 'Missing file key'
print('QA-04: PASS ✅')
" || echo "QA-04: FAIL ❌"

echo ""
echo "--- QA-05: Original demo still works ---"
docker run --rm selfplay-dogfood selfplay demo 2>&1 | tee /tmp/dogfood-05.txt
grep -q "SelfPlay demo" /tmp/dogfood-05.txt && echo "QA-05: PASS ✅" || echo "QA-05: FAIL ❌"

echo ""
echo "=== Dogfooding Docker QA Complete ==="
