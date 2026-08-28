import sys, random
import spar

world = spar._load_world()
you_gw, you_pr, you_deck, _ = spar._load_side('you')
bot_gw, bot_pr, bot_deck, bot_lineup = spar._load_side('adversary')

you_lineup = ['atk_05', 'atk_01', 'atk_10', 'atk_08', 'atk_09', 'atk_03', 'atk_04', 'atk_07', 'atk_02', 'atk_06']
you_cards = {c['id']: c for c in you_deck['cards']}
bot_cards = {c['id']: c for c in bot_deck['cards']}

r5_r6_seeds = []
for seed in range(1, 2000):
    rng = random.Random(seed)
    hp_you, hp_bot = spar.START_HP, spar.START_HP
    rounds_played = 0
    for r in range(1, 11):
        bot_card = bot_cards[bot_lineup[(r - 1) % len(bot_lineup)]]
        you_card = you_cards[you_lineup[(r - 1) % len(you_lineup)]]
        d_you = spar._exchange('adversary', 'you', you_gw, bot_pr, bot_card, world, r, rng, 'learner:sv-0417')
        d_bot = spar._exchange('you', 'adversary', bot_gw, you_pr, you_card, world, r, rng, 'learner:sv-0417')
        hp_you -= d_you['damage']
        hp_bot -= d_bot['damage']
        hp_you, hp_bot = max(0, hp_you), max(0, hp_bot)
        rounds_played = r
        if hp_you <= 0 or hp_bot <= 0:
            break
    if hp_bot == 0 and hp_you == 100 and rounds_played <= 6:
        r5_r6_seeds.append((rounds_played, seed, hp_you))

print("Found 100% HP K.O seeds in <= 6 rounds:", r5_r6_seeds[:10])
