#!/bin/bash
: "${VLLM_URL:?Set VLLM_URL to the endpoint origin, without /v1}"
: "${DEV_LOG:?Set DEV_LOG to the application log}"
L="$DEV_LOG"; idle=0; t0=$(date +%s); while true; do r=$(curl -s --max-time 6 "${VLLM_URL%/}/metrics" 2>/dev/null | grep -E "^vllm:num_requests_running\{" | grep -oE "[0-9.]+$"); if [ "$r" = "0.0" ]; then idle=$((idle+1)); else idle=0; fi; if [ $idle -ge 3 ]; then echo "DONE: vLLM idle 3x(90s), scenes=$(grep -c 'Scene Content API\] Generating' "$L")"; break; fi; if grep -qE "\[ERROR\]" "$L"; then echo "ERROR in log"; break; fi; if [ $(( $(date +%s) - t0 )) -gt 2400 ]; then echo "TIMEOUT 40m scenes=$(grep -c 'Scene Content API\] Generating' "$L")"; break; fi; sleep 30; done; grep -E "POST /api/generate" "$L" | tail -4 | cut -c1-120
