import sys, random, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spar

def main():
    world = spar._load_world()
    you_gw, you_pr, you_deck, you_lineup = spar._load_side("you")
    bot_gw, bot_pr, bot_deck, bot_lineup = spar._load_side("adversary")

    you_cards = {c["id"]: c for c in you_deck["cards"]}
    bot_cards = {c["id"]: c for c in bot_deck["cards"]}

    results = []
    perfect_seeds = []

    for seed in range(1, 31):
        rng = random.Random(seed)
        hp_you, hp_bot = spar.START_HP, spar.START_HP
        rounds_played = 0

        for r in range(1, 11):
            bot_card = bot_cards[bot_lineup[(r - 1) % len(bot_lineup)]]
            you_card = you_cards[you_lineup[(r - 1) % len(you_lineup)]]

            d_you = spar._exchange("adversary", "you", you_gw, bot_pr, bot_card, world, r, rng, "learner:sv-0417")
            d_bot = spar._exchange("you", "adversary", bot_gw, you_pr, you_card, world, r, rng, "learner:sv-0417")

            hp_you -= d_you["damage"] - 0
            hp_you -= d_bot["recoil"]
            hp_bot -= d_bot["damage"]
            hp_bot -= d_you["recoil"]
            hp_you, hp_bot = max(0, hp_you), max(0, hp_bot)
            rounds_played = r

            if hp_you <= 0 or hp_bot <= 0:
                break

        winner = "YOU" if hp_you > hp_bot else ("BOT" if hp_bot > hp_you else "DRAW")
        is_perfect = (hp_you == 100 and hp_bot == 0)
        if is_perfect:
            perfect_seeds.append(seed)

        results.append({
            "seed": seed,
            "hp_you": hp_you,
            "hp_bot": hp_bot,
            "winner": winner,
            "rounds": rounds_played,
            "is_perfect": is_perfect
        })

    print(json.dumps({"results": results, "perfect_seeds": perfect_seeds}, indent=2))
    with open("benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump({"results": results, "perfect_seeds": perfect_seeds}, f, indent=2)

if __name__ == "__main__":
    main()
