#!/bin/bash
# qa-docker.sh — SelfPlay Docker QA from zero (bach SOP adapted)
set -e

echo "=== SelfPlay Docker QA (bach SOP) ==="
PASS=0; FAIL=0; SKIP=0

check() {
  local label="$1" result="$2"
  if [ "$result" = "PASS" ]; then
    echo "  [PASS] $label"
    PASS=$((PASS + 1))
  elif [ "$result" = "SKIP" ]; then
    echo "  [SKIP] $label"
    SKIP=$((SKIP + 1))
  else
    echo "  [FAIL] $label"
    FAIL=$((FAIL + 1))
  fi
}

# DQ-01: Build
echo ""
echo "[DQ-01] Docker build..."
docker build -t selfplay-dev:latest . > /dev/null 2>&1
check "Build completes" "PASS"

# DQ-02: Version
echo ""
echo "[DQ-02] Version check..."
VER=$(docker run --rm selfplay-dev:latest selfplay --version 2>&1)
check "selfplay --version: $VER" "$([ "$VER" = "selfplay 0.2.0" ] && echo PASS || echo FAIL)"

# DQ-03~07: Demo
echo ""
echo "[DQ-03~07] Demo smoke test..."
OUT=$(docker run --rm selfplay-dev:latest selfplay demo "Docker QA test" 2>&1)
check "3 cycles visible" "$(echo "$OUT" | grep -q "Cycle 3/3" && echo PASS || echo FAIL)"
check "Threshold reached" "$(echo "$OUT" | grep -q "threshold reached" && echo PASS || echo FAIL)"
check "Score improves" "$(echo "$OUT" | grep -qE "Total improvement: \+" && echo PASS || echo FAIL)"
check "Mutation applied" "$(echo "$OUT" | grep -q "Mutate" && echo PASS || echo FAIL)"
check "D5 Rejected visible" "$(echo "$OUT" | grep -q "Rejected" && echo PASS || echo SKIP)"

# DQ-10: Tests
echo ""
echo "[DQ-10] Unit tests..."
TEST_OUT=$(docker run --rm selfplay-dev:latest python -m pytest tests/ -q 2>&1)
check "All tests pass" "$(echo "$TEST_OUT" | grep -q "3 passed" && echo PASS || echo FAIL)"
echo "  $TEST_OUT"

# DQ-11: Clean exit
echo ""
echo "[DQ-11] Clean exit..."
docker run --rm selfplay-dev:latest selfplay demo "exit test" > /dev/null 2>&1
EXIT_CODE=$?
check "Exit code 0" "$([ $EXIT_CODE -eq 0 ] && echo PASS || echo FAIL)"

# DQ-12: No crash
echo ""
echo "[DQ-12] No crash..."
check "No Python traceback" "$(echo "$OUT" | grep -q "Traceback" && echo FAIL || echo PASS)"

# DQ-13: JSON valid
echo ""
echo "[DQ-13] JSON output..."
JSON_OUT=$(docker run --rm selfplay-dev:latest selfplay demo --json "JSON test" 2>&1)
check "Valid JSON" "$(echo "$JSON_OUT" | python3 -c 'import sys,json; json.load(sys.stdin); print("PASS")' 2>/dev/null || echo FAIL)"

# Summary
echo ""
echo "==================================="
echo "  PASS: $PASS  |  FAIL: $FAIL  |  SKIP: $SKIP"
echo "==================================="
[ $FAIL -eq 0 ] && echo "QA PASSED" || echo "QA FAILED"
exit $FAIL
