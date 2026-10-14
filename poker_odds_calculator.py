import random
from collections import Counter

RANKS = "23456789TJQKA"
SUITS = "SHDC"
DECK = [r + s for r in RANKS for s in SUITS]

HANDS = [
    "Five of a Kind",
    "Royal Flush",
    "Straight Flush",
    "Four of a Kind",
    "Full House",
    "Flush",
    "Straight",
    "Three of a Kind",
    "Two Pair",
    "One Pair",
    "High Card"
]

RUNS = 50000
MAX_DECKS = 10000


def read_decks():
    while True:
        a = input("Number of decks (or 'inf' for infinite): ").strip().lower()
        if a in ["inf", "infinite", "infinity", "∞"]:
            return None

        try:
            n = int(a)
            if 1 <= n <= MAX_DECKS:
                return n
            print(f"Please enter a whole number from 1 to {MAX_DECKS}, or inf.")
        except ValueError:
            print("That isn't a valid number. Try 1, 2, 3, etc., or inf.")


def fix_card(s):
    s = s.strip().upper()
    for symbol, letter in [("♠", "S"), ("♥", "H"), ("♦", "D"), ("♣", "C")]:
        s = s.replace(symbol, letter)

    if len(s) < 2:
        raise ValueError(f"'{s}' is not a card.")

    rank = s[:-1]
    suit = s[-1]
    if rank == "10":
        rank = "T"

    if rank not in RANKS or suit not in SUITS:
        raise ValueError(f"'{s}' is invalid. Example cards: AS, 10H, 7D, KC.")
    return rank + suit


def ask_cards(title, amt, old, n):
    while True:
        print(f"\nEnter {amt} card(s) for {title} (separate with spaces or commas).")
        line = input("> ").strip()
        if line.lower() in ["q", "quit", "exit"]:
            raise SystemExit
        parts = line.replace(",", " ").replace(";", " ").split()

        if len(parts) != amt:
            print(f"Expected exactly {amt} card(s), but got {len(parts)}. Try again.")
            continue

        try:
            new = [fix_card(x) for x in parts]
        except ValueError as e:
            print(e)
            continue

        if n is not None:
            cc = Counter(old + new)
            wrong = [c for c, count in cc.items() if count > n]
            if wrong:
                print(f"Too many copies of {', '.join(wrong)}. With {n} deck(s), "
                      f"you can only use each exact card {n} time(s).")
                continue

        return new


def has_straight(ranks):
    v = set(ranks)
    if 14 in v:
        v.add(1)
    for start in range(1, 11):
        if all(x in v for x in range(start, start + 5)):
            return True
    return False


def hand_type(cards):
    vals = [RANKS.index(c[0]) + 2 for c in cards]
    suits = [c[1] for c in cards]
    rc = Counter(vals)
    sc = Counter(suits)

    if max(rc.values()) >= 5:
        return "Five of a Kind"

    for s in SUITS:
        if sc[s] >= 5:
            same = [vals[i] for i in range(len(cards)) if suits[i] == s]
            if {10, 11, 12, 13, 14}.issubset(set(same)):
                return "Royal Flush"
            if has_straight(same):
                return "Straight Flush"

    if max(rc.values()) >= 4:
        return "Four of a Kind"

    for v in rc:
        if rc[v] >= 3 and any(rc[x] >= 2 for x in rc if x != v):
            return "Full House"

    if max(sc.values()) >= 5:
        return "Flush"
    if has_straight(vals):
        return "Straight"
    if max(rc.values()) >= 3:
        return "Three of a Kind"
    if sum(x >= 2 for x in rc.values()) >= 2:
        return "Two Pair"
    if max(rc.values()) >= 2:
        return "One Pair"
    return "High Card"


def calculate(known, n):
    missing = 7 - len(known)
    ans = Counter()

    if missing == 0:
        ans[hand_type(known)] += 1
        return ans, 1, "Exact"

    # One or two cards calculations
    if missing <= 2:
        left = {c: (1 if n is None else n) for c in DECK}
        if n is not None:
            for c in known:
                left[c] -= 1

        if missing == 1:
            for a in DECK:
                ways = 1 if n is None else left[a]
                if ways > 0:
                    ans[hand_type(known + [a])] += ways
        else:
            for i, a in enumerate(DECK):
                for b in DECK[i:]:
                    if n is None:
                        ways = 1 if a == b else 2
                    elif a == b:
                        ways = left[a] * (left[a] - 1) // 2
                    else:
                        ways = left[a] * left[b]

                    if ways > 0:
                        ans[hand_type(known + [a, b])] += ways
        return ans, sum(ans.values()), "Exact"

    # Randomly finish the hand many times
    if n is not None:
        remaining = DECK * n
        for c in known:
            remaining.remove(c)

    for i in range(RUNS):
        if n is None:
            extra = random.choices(DECK, k=missing)
        else:
            extra = random.sample(remaining, missing)
        ans[hand_type(known + extra)] += 1

    return ans, RUNS, "Simulated"


def show_results(known, n, stage):
    counts, total, kind = calculate(known, n)
    print("\n" + "=" * 49)
    print(stage.upper())
    print("Cards so far:", " ".join(known))
    if len(known) >= 5:
        print("Best hand right now:", hand_type(known))
    else:
        print("Best hand right now: not enough cards yet")

    if kind == "Exact":
        print(f"Final 7-card hand probabilities (exact, {total:,} outcomes)")
    else:
        print(f"Final 7-card hand probabilities (estimate, {total:,} simulations)")
    print("-" * 49)
    for h in HANDS:
        pct = counts[h] / total * 100
        print(f"{h:<21} {pct:>11.5f}%")
    print("=" * 49)


def main():
    print("POKER HAND PROBABILITY CALCULATOR")
    print("Cards: AS = Ace of Spades, 10H = Ten of Hearts, etc.")
    print("S=Spades, H=Hearts, D=Diamonds, C=Clubs")
    print("Type q when entering cards to quit.\n")
    print("Odds are for the BEST 5-card hand out of the final 7 cards.")
    print("Multiple decks allow repeated cards\n")

    n = read_decks()
    known = []

    for stage, qty in [("Hole Cards", 2), ("Flop", 3), ("Turn", 1), ("River", 1)]:
        new = ask_cards(stage, qty, known, n)
        known.extend(new)
        show_results(known, n, stage)

    print("\nFinished! The river result is now your final hand.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nStopped.")
