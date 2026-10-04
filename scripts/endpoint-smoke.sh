#!/bin/bash
# Model listing and a neutral synthetic completion; no original course prompt.
set -o pipefail
: "${VLLM_URL:?Set VLLM_URL to the endpoint origin, without /v1}"
: "${MODEL:?Set MODEL to the served model identifier}"
echo "Models"
curl -fsS --max-time 8 "${VLLM_URL%/}/v1/models" |
  python3 -c 'import sys,json; d=json.load(sys.stdin); [print(m["id"]) for m in d.get("data",[])]' || exit 1
echo "Synthetic completion"
payload=$(python3 -c 'import json,os; print(json.dumps({"model":os.environ["MODEL"],"messages":[{"role":"user","content":"Return a brief acknowledgement."}],"max_tokens":16}))')
curl -fsS --max-time 30 "${VLLM_URL%/}/v1/chat/completions" \
  -H "Content-Type: application/json" -d "$payload" |
  python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["choices"][0]["message"]["content"][:40])'
