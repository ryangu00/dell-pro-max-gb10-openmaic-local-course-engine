#!/bin/bash
: "${VLLM_URL:?Set VLLM_URL to the endpoint origin, without /v1}"
: "${DEV_LOG:?Set DEV_LOG to the application log}"
# The first tok_delta is a cumulative baseline, not a per-minute sample.
# Discard it when computing rates; the source monitor starts prev_tok at zero.
L="$DEV_LOG"
prev_tok=0; stall=0; t0=$(date +%s)
while true; do
  tok=$(curl -s --max-time 6 "${VLLM_URL%/}/metrics" 2>/dev/null | grep -E "^vllm:generation_tokens_total\{" | grep -oE "[0-9.e+]+$" | python3 -c "import sys; print(int(float(sys.stdin.read().strip() or 0)))" 2>/dev/null || echo 0)
  run=$(curl -s --max-time 6 "${VLLM_URL%/}/metrics" 2>/dev/null | grep -E "^vllm:num_requests_running\{" | grep -oE "[0-9.]+$" || echo "?")
  scenes=$(grep -c "Scene Content API\] Generating" "$L")
  errs=$(grep -cE "\[ERROR\]" "$L")
  delta=$((tok - prev_tok)); prev_tok=$tok
  el=$(( ($(date +%s) - t0) / 60 ))
  if [ $delta -le 0 ] && [ "$run" != "1.0" ]; then stall=$((stall+1)); else stall=0; fi
  echo "[+${el}m] scenes_started=$scenes err=$errs vllm_running=$run tok_delta=$delta stall=$stall"
  if grep -qiE "\[INFO\].*(all scenes|course (saved|complete|ready)|generation complete)" "$L"; then echo "DONE_SIGNAL"; break; fi
  if [ $errs -gt 0 ]; then echo "ERROR_SIGNAL"; break; fi
  if [ $stall -ge 3 ]; then echo "STALL_3x_NO_TOKEN_NO_RUNNING"; break; fi
  if [ $el -ge 30 ]; then echo "TIMEOUT_30m"; break; fi
  sleep 60
done
