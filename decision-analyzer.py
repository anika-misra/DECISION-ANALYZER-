import math
import random
import time

random.seed(time.time())

POSITIVE_HINTS = {
    "positive": ["good", "benefit", "beneficial", "gain", "profit", "win", "comfortable", "easy", "safe"],
    "opportunity": ["opportunity", "chance", "growth", "learn", "improve", "advance"],
}
NEGATIVE_HINTS = {
    "risk": ["risk", "risky", "danger", "problem", "loss", "hard", "difficult", "expensive", "stress"],
    "uncertainty": ["maybe", "might", "could", "if", "uncertain", "unclear"],
}
def clean_text(s: str) -> str:
    """Lowercase and remove obvious punctuation for simple token checks."""
    return ''.join(ch.lower() if ch.isalnum() or ch.isspace() else ' ' for ch in s).strip()

def word_count(s: str) -> int:
    return len(s.split())

def sentiment_hint_score(s: str) -> int:
    """Simple sentiment-like heuristic using presence of words in our lists."""
    t = clean_text(s)
    score = 0
    for w in POSITIVE_HINTS["positive"]:
        if w in t: score += 2
    for w in POSITIVE_HINTS["opportunity"]:
        if w in t: score += 1
    for w in NEGATIVE_HINTS["risk"]:
        if w in t: score -= 2
    for w in NEGATIVE_HINTS["uncertainty"]:
        if w in t: score -= 1
    return score

def clarity_score(s: str) -> int:
    """Short, clear phrases are often easier to decide on; penalize extreme length."""
    wc = word_count(s)
    if wc <= 4:
        return 1   
    if wc <= 12:
        return 3   
    if wc <= 25:
        return 2   
    return 0       

def pros_cons_inference(s: str) -> int:
    """
    Try to infer 'pros' or 'cons' style words (very simple).
    Give small boost if phrase contains 'because', 'so', 'therefore' (reasoning).
    """
    t = clean_text(s)
    score = 0
    if "because" in t or "since" in t or "therefore" in t:
        score += 2
    
    if "pro" in t or "advantage" in t:
        score += 1
    if "con" in t or "disadvantage" in t:
        score -= 1
    return score

def risk_adjustment(s: str) -> float:
    """Return a fractional multiplier <1 if there are many risk words."""
    t = clean_text(s)
    risks = sum(1 for w in NEGATIVE_HINTS["risk"] if w in t)
    uncs = sum(1 for w in NEGATIVE_HINTS["uncertainty"] if w in t)
    penalty = 1.0 - min(0.4, 0.12 * risks + 0.06 * uncs)  # at most ~40% penalty
    return max(0.6, penalty)

def human_like_randomness() -> float:
    """A small, skewed random factor to mimic human indecisiveness."""
    
    r = random.random()
    if r < 0.08:
        return 1 + random.uniform(0.08, 0.22)  
    return 1 + random.uniform(-0.06, 0.08)    

def score_situation(s: str) -> dict:
    """Compute multiple components and combine into a final numeric score."""
    components = {}
    components['raw_length'] = word_count(s)
    components['clarity'] = clarity_score(s)
    components['sentiment_hint'] = sentiment_hint_score(s)
    components['reasoning_hint'] = pros_cons_inference(s)
    components['risk_mult'] = risk_adjustment(s)
    components['random_mult'] = human_like_randomness()
    
    
    base = components['clarity'] * 1.5 + components['sentiment_hint'] + components['reasoning_hint']
    
    
    final = base * components['risk_mult'] * components['random_mult']
 
    final_score = round(final, 3)
    components['final_score'] = final_score
    return components

def explain_choice(s1, c1, s2, c2):
 
    def print_comp(i, s, c):
        print(f"\nOption {i}: \"{s}\"")
        print(f"  - words: {c['raw_length']}, clarity: {c['clarity']}, "
              f"sentiment_hint: {c['sentiment_hint']}, reasoning_hint: {c['reasoning_hint']}")
        print(f"  - risk multiplier: {c['risk_mult']:.2f}, human sway: {c['random_mult']:.2f}")
        print(f"  => combined score: {c['final_score']}")
    print_comp(1, s1, c1)
    print_comp(2, s2, c2)

    
    diff = c1['final_score'] - c2['final_score']
    print("\n--- Final Thought ---")
    if abs(diff) < 0.15:
        print("Both options look quite close. I'd lean slightly toward the one with clearer reasoning or fewer risks.")
    elif diff > 0:
        print("Option 1 seems better based on clarity/positives and lower inferred risk.")
    else:
        print("Option 2 seems better based on clarity/positives and lower inferred risk.")

def main():
    print("Welcome — I will help you decide between two situations.")
    print("Please describe each situation in one or two sentences (keep it natural).")
    s1 = input("\nEnter Situation 1: ").strip()
    s2 = input("Enter Situation 2: ").strip()


    if not s1 or not s2:
        print("Both situations must be provided. Restart and give two short descriptions.")
        return

    print("\nThinking... (I will explain my steps so you can analyze them)")
    c1 = score_situation(s1)
    c2 = score_situation(s2)


    explain_choice(s1, c1, s2, c2)


    if c1['final_score'] > c2['final_score'] + 0.12:
        print(f"\n>>> My pick: Situation 1 — \"{s1}\" (reasoned choice based on the above).")
    elif c2['final_score'] > c1['final_score'] + 0.12:
        print(f"\n>>> My pick: Situation 2 — \"{s2}\" (reasoned choice based on the above).")
    else:
    
        print("\n>>> It's a near tie. Both options have merits.")
       
        tie_break = random.choice([1, 2])
        print(f"I'd nudge you toward Option {tie_break} if you need to decide now; "
              "but consider adding one practical test (small experiment) to compare them.")

if __name__ == "__main__":
    main()
