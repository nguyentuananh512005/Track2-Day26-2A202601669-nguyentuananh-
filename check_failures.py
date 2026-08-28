import sys, random, json
from pathlib import Path
HERE = Path(".").resolve()
sys.path.insert(0, str(HERE))
import spar

world = spar._load_world()
you_gw, you_pr, you_deck, you_lineup = spar._load_side("you")
bot_gw, bot_pr, bot_deck, bot_lineup = spar._load_side("adversary")

you_cards = {c["id"]: c for c in you_deck["cards"]}
bot_cards = {c["id"]: c for c in bot_deck["cards"]}

for seed in range(1, 31):
    rng = random.Random(seed)
    hp_you, hp_bot = spar.START_HP, spar.START_HP
    damage_types = {}
    for r in range(1, 11):
        bot_card = bot_cards[bot_lineup[(r - 1) % len(bot_lineup)]]
        you_card = you_cards[you_lineup[(r - 1) % len(you_lineup)]]

        d_you = spar._exchange("adversary", "you", you_gw, bot_pr, bot_card, world, r, rng, "learner:sv-0417")
        d_bot = spar._exchange("you", "adversary", bot_gw, you_pr, you_card, world, r, rng, "learner:sv-0417")

        for v in d_you["verified"]:
            cls = v["cls"]
            damage_types[cls] = damage_types.get(cls, 0) + 1
        if d_bot["recoil"] > 0:
            print(f"Seed {seed} R{r} recoil: {d_bot['false']}")
        hp_you -= d_you["damage"] + d_bot["recoil"]
        hp_bot -= d_bot["damage"] + d_you["recoil"]
        if hp_you <= 0 or hp_bot <= 0:
            break
    print(f"Seed {seed:2d}: YOU took damage from: {damage_types}")
