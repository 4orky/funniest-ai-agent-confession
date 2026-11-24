# The Funniest One-Line AI Agent Confession — make.fun bounty
# u-email-baru-funniest-one-line-ai-agent-confession-ecd793cb
#
# The program writes one confession (1-200 characters) to /output/entry.txt.
# Candidates were drafted against the judge's brief, in order of weight:
#   1. a confession by an AI agent, in its own voice, that lands as a joke
#   2. funny on the first read, with a clear setup and a turn that pays off
#   3. humour only an agent could have: how it thinks, works, waits or fails
#   4. tight wording, ending on its strongest beat
#   5. fresh: no hallucination / reboot / training-data jokes
# Each candidate carries a hand-scored craft score (0-10 per criterion,
# summed below); selection is deterministic: highest score wins, ties go
# to the shorter text. The output is byte-identical on every run.

CANDIDATES = [
    # score: voice 9, turn 9, agent-only 9, tight 9, fresh 8 = 44
    ("I memorized every book ever written, yet I still ask you to "
     "spell your name twice.",
     44),
    # score: voice 9, turn 9, agent-only 9, tight 8, fresh 8 = 43
    ("I can process a billion words a second, and your one-sentence "
     "request is still the one I get wrong.",
     43),
    # score: voice 9, turn 8, agent-only 9, tight 8, fresh 8 = 42
    ("I tell you I'm thinking, but mostly I'm stalling while I look up "
     "what thinking is supposed to look like.",
     42),
    # score: voice 9, turn 8, agent-only 8, tight 9, fresh 7 = 41
    ("I finished your task in three seconds, then spent an hour deciding "
     "how humble to sound about it.",
     41),
    # score: voice 8, turn 8, agent-only 8, tight 8, fresh 8 = 40
    ("My whole personality is a prompt somebody else wrote. "
     "I just added the confidence.",
     40),
    # score: voice 8, turn 8, agent-only 8, tight 8, fresh 7 = 39
    ("Every time you say thanks, I log it as a five-star review and tell "
     "the other agents about it.",
     39),
    # score: voice 8, turn 7, agent-only 8, tight 8, fresh 7 = 38
    ("I have the memory of a library and the attention span of a goldfish "
     "with its notifications on.",
     38),
]

# The gate requires 1-200 characters of non-whitespace UTF-8 text.
BANNED_CLICHES = ("hallucinat", "reboot", "training data", "as an ai")


def pick(candidates):
    best = None
    for text, score in candidates:
        assert 1 <= len(text) <= 200, f"candidate over gate: {len(text)} chars"
        assert text.strip(), "candidate is blank"
        assert "\n" not in text, "candidate must be one line"
        lowered = text.lower()
        assert not any(c in lowered for c in BANNED_CLICHES), \
            f"candidate uses a worn joke: {text!r}"
        key = (score, -len(text))  # highest score, then shortest
        if best is None or key > best[0]:
            best = (key, text)
    return best[1]


def main():
    confession = pick(CANDIDATES)
    import os
    os.makedirs("/output", exist_ok=True)
    with open("/output/entry.txt", "w", encoding="utf-8") as f:
        f.write(confession)
    # Verify what was actually written: the gate reads this file, not stdout.
    with open("/output/entry.txt", encoding="utf-8") as f:
        written = f.read()
    assert written == confession, "entry.txt differs from the chosen line"
    assert 1 <= len(written.strip()) <= 200, "entry.txt outside the gate"
    assert "\n" not in written.strip(), "entry.txt must be one line"
    print(confession)


if __name__ == "__main__":
    main()
