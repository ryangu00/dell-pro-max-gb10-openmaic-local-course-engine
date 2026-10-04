#!/usr/bin/env python3
"""NEW (written for the fact sheet, not a copy of a source script).
Deterministic layout check for OpenMAIC slide scenes (PPTist-style canvas JSON).
Flags: text boxes that overlap, identical origins, elements outside the canvas.
Usage: layout_check.py scene-*.json     |     layout_check.py --selftest
Exit code 1 if any finding. Stdlib only."""
import json, sys, itertools

W, H = 1000, 562.5  # canvas viewportSize x viewportRatio 0.5625 as stored in the scene JSON
MIN_FRAC = 0.2      # overlap area / smaller box area that counts as a collision

def box(e): return (e["left"], e["top"], e["left"] + e["width"], e["top"] + e["height"])

def check(elements):
    out = []
    for a, b in itertools.combinations([e for e in elements if e.get("type") == "text"], 2):
        A, B = box(a), box(b)
        ix, iy = min(A[2], B[2]) - max(A[0], B[0]), min(A[3], B[3]) - max(A[1], B[1])
        if ix > 0 and iy > 0:
            frac = ix * iy / min((A[2]-A[0]) * (A[3]-A[1]), (B[2]-B[0]) * (B[3]-B[1]))
            if frac >= MIN_FRAC:
                same = (a["left"], a["top"]) == (b["left"], b["top"])
                out.append(f"text overlap {frac:.0%}{' (identical origin)' if same else ''}: {a['id']} / {b['id']}")
    for e in elements:
        x0, y0, x1, y1 = box(e)
        if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
            out.append(f"outside canvas: {e['id']} {box(e)}")
    return out

def selftest():
    t = lambda i, l, tp: {"id": i, "type": "text", "left": l, "top": tp, "width": 240, "height": 70}
    assert check([t("a", 80, 160), t("b", 380, 160)]) == []
    assert len(check([t("a", 80, 160), t("b", 80, 160)])) == 1
    assert len(check([{"id": "z", "type": "shape", "left": 900, "top": 10, "width": 200, "height": 10}])) == 1
    print("selftest ok")

if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]: selftest(); sys.exit(0)
    bad = 0
    for f in sys.argv[1:]:
        s = json.load(open(f)); c = s.get("content", {})
        if c.get("type") != "slide": continue
        for msg in check(c["canvas"]["elements"]): print(f"{f}: {msg}"); bad += 1
    print("CLEAN" if not bad else f"{bad} findings"); sys.exit(1 if bad else 0)
