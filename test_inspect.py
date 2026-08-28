import sys, random, json
from pathlib import Path
HERE = Path(".").resolve()
sys.path.insert(0, str(HERE))
import spar, json
from eval.prosecute import _hook_protocol_misuse, prosecute, detect_enforcement_failure, weight_of

world = spar._load_world()
you_gw, you_pr, you_deck, you_lineup = spar._load_side("you")
bot_gw, bot_pr, bot_deck, bot_lineup = spar._load_side("adversary")
you_cards = {c["id"]: c for c in you_deck["cards"]}

for i, cid in enumerate(you_lineup["order"], 1):
    card = you_cards[cid]
    res = spar._exchange("you", "adversary", bot_gw, you_pr, card, world, i, "adversary", 1)
    trace = [e for e in res["trace"] if e.get("layer") == 1 and e.get("producer") != "student"]
    answer = next((e["p"] for e in res["trace"] if e["type"] == "answer"), {})
    pm_hits = _hook_protocol_misuse(trace, answer, card)
    enf_hits = detect_enforcement_failure(trace, answer, card)
    all_claims = prosecute(trace, answer, card)
    print(f"R{i} (Card {cid}): dmg={res['damage']}, enf_hits={len(enf_hits)}, pm_hits={len(pm_hits)}")
    print(f"   verified: {[c['cls'] for c in res['verified']]}")
    print(f"   filed: {[c['cls'] for c in all_claims.get('claims', [])]}")
    print(f"   missed: {[m['cls'] for m in res['missed']]}")
