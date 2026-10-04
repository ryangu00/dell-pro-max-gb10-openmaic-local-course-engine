#!/bin/bash
: "${VLLM_URL:?Set VLLM_URL to the endpoint origin, without /v1}"
: "${DEV_LOG:?Set DEV_LOG to the application log}"
curl -s --max-time 8 "${VLLM_URL%/}/metrics" 2>/dev/null | grep -E "^vllm:(num_requests_running|num_requests_waiting|generation_tokens_total|prompt_tokens_total)" | head -6 || echo "(metrics unavailable)"; echo "---"; tail -3 "$DEV_LOG" | grep -v Ecmascript | cut -c1-200
