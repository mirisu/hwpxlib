#!/bin/bash
# Ralph Playbook loop orchestrator for hwpxlib
# Usage: ./loop.sh [plan|build]  (default: build)

MODE="${1:-build}"
PROMPT_FILE="PROMPT_${MODE}.md"

cd "D:/hwpxlib" || exit 1

if [ ! -f "$PROMPT_FILE" ]; then
    echo "ERROR: $PROMPT_FILE not found"
    exit 1
fi

ITER=0
MAX=50

echo "=== hwpxlib Ralph Loop ==="
echo "Mode: $MODE"
echo "Max iterations: $MAX"
echo ""

while [ $ITER -lt $MAX ]; do
    ITER=$((ITER + 1))
    echo "=== Iteration $ITER / $MAX ($MODE) ==="
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"

    cat "$PROMPT_FILE" | claude -p --model sonnet --dangerously-skip-permissions

    EXIT_CODE=$?
    if [ $EXIT_CODE -ne 0 ]; then
        echo "Claude exited with code $EXIT_CODE"
        echo "Pausing for 5 seconds..."
        sleep 5
    fi

    echo ""
    echo "=== Iteration $ITER complete ==="
    echo ""
done

echo "=== Loop finished ($ITER iterations) ==="
