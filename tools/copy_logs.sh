#!/bin/bash

AGENTS=("verity" "nova" "right" "breeze" "ripple" "minty")

for AGENT in "${AGENTS[@]}"; do
    SRC_DIR=~/verityos/memory_system/$AGENT
    DEST_DIR=~/verityos/fine_tuning/$AGENT/raw_logs

    if [ -d "$SRC_DIR" ]; then
        cp -v "$SRC_DIR"/*.json "$DEST_DIR"/ 2>/dev/null
        echo "✅ Copied logs for $AGENT"
    else
        echo "⚠️  No memory directory for $AGENT found at $SRC_DIR"
    fi
done