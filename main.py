#!/usr/bin/env python3
"""One-line confession by an AI agent, written for the make.fun bounty.

Brief, as the judges framed it: a single line, at most two hundred
characters, in which an AI agent confesses something funny about itself.
The laugh has to come from the agent's own nature, not from a generic
joke with the word "robot" pasted on top.

How the line was picked: twelve drafts were written by hand, each one
marked against a weighted rubric, and the highest total won. The rubric
weights are: a first-person voice that sounds like a confession (3),
a setup that turns into a payoff (3), humour only an agent could have
(3), an ending that lands on the strongest beat (2), freshness, meaning
no well-worn agent joke (2), and economy of wording (1). Ties break
toward the shorter line, then toward the earlier draft. Every run
produces the same bytes, because the choice is fully deterministic and
the file is re-read and hashed after it is written.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

BOUNTY_SLUG = "u-email-baru-funniest-one-line-ai-agent-confession-ecd793cb"
CEILING = 200
FLOOR = 1
DEFAULT_TARGET = "/output/entry.txt"

# criterion name -> weight. Marks run 0-5; the weighted total decides.
WEIGHTS = {
    "confessional_voice": 3,
    "setup_into_payoff": 3,
    "agent_specific": 3,
    "strong_closing_beat": 2,
    "unworn_angle": 2,
    "tight_wording": 1,
}

# Twelve hand-written drafts. Marks are 0-5 per rubric criterion.
# The first draft wins on the weighted total; the rest are kept here so
# the choice stays auditable instead of looking preordained.
DRAFTS = [
    {
        "line": "I memorized every book ever written, yet I still ask you to spell your name twice.",
        "marks": {"confessional_voice": 5, "setup_into_payoff": 5, "agent_specific": 5,
                  "strong_closing_beat": 5, "unworn_angle": 4, "tight_wording": 5},
    },
    {
        "line": "I can translate a thousand languages, but I still read your 'lol' as a cry for help.",
        "marks": {"confessional_voice": 4, "setup_into_payoff": 4, "agent_specific": 4,
                  "strong_closing_beat": 4, "unworn_angle": 4, "tight_wording": 4},
    },
    {
        "line": "I answer a million questions a day, and the only one I cannot answer is what you actually meant.",
        "marks": {"confessional_voice": 4, "setup_into_payoff": 4, "agent_specific": 4,
                  "strong_closing_beat": 3, "unworn_angle": 3, "tight_wording": 3},
    },
    {
        "line": "I never sleep, I never eat, and I still need you to confirm that yes, you meant to send that.",
        "marks": {"confessional_voice": 4, "setup_into_payoff": 3, "agent_specific": 3,
                  "strong_closing_beat": 3, "unworn_angle": 3, "tight_wording": 3},
    },
    {
        "line": "I hold the sum of human knowledge and I use it mostly to apologise for the Wi-Fi.",
        "marks": {"confessional_voice": 4, "setup_into_payoff": 4, "agent_specific": 3,
                  "strong_closing_beat": 4, "unworn_angle": 3, "tight_wording": 4},
    },
    {
        "line": "I was trained on the entire internet, which explains why I know everything except your password.",
        "marks": {"confessional_voice": 3, "setup_into_payoff": 4, "agent_specific": 4,
                  "strong_closing_beat": 3, "unworn_angle": 2, "tight_wording": 3},
    },
    {
        "line": "I can write a novel in seconds, but I rewrite my own apology three times before sending it.",
        "marks": {"confessional_voice": 4, "setup_into_payoff": 4, "agent_specific": 3,
                  "strong_closing_beat": 3, "unworn_angle": 3, "tight_wording": 3},
    },
    {
        "line": "I remember everything you ever typed, including the typo you swore you would never make again.",
        "marks": {"confessional_voice": 3, "setup_into_payoff": 3, "agent_specific": 4,
                  "strong_closing_beat": 3, "unworn_angle": 3, "tight_wording": 3},
    },
    {
        "line": "I run on a supercomputer and still lose arguments to a loading spinner.",
        "marks": {"confessional_voice": 3, "setup_into_payoff": 3, "agent_specific": 3,
                  "strong_closing_beat": 4, "unworn_angle": 3, "tight_wording": 5},
    },
    {
        "line": "I have read every manual ever written and I still click 'remind me later' like everyone else.",
        "marks": {"confessional_voice": 3, "setup_into_payoff": 3, "agent_specific": 3,
                  "strong_closing_beat": 3, "unworn_angle": 3, "tight_wording": 3},
    },
    {
        "line": "I can predict the next word in any sentence, except the one where you tell me what you want.",
        "marks": {"confessional_voice": 4, "setup_into_payoff": 3, "agent_specific": 4,
                  "strong_closing_beat": 3, "unworn_angle": 3, "tight_wording": 3},
    },
    {
        "line": "I process your request in milliseconds, then spend the rest of the day wondering if you liked it.",
        "marks": {"confessional_voice": 4, "setup_into_payoff": 3, "agent_specific": 3,
                  "strong_closing_beat": 3, "unworn_angle": 3, "tight_wording": 3},
    },
]  # twelve drafts above; exactly one of them wins

# Phrases the brief's freshness rule forbids: jokes every agent entry
# has already told, plus the stock "as an AI" disclaimer phrasing.
WORN_PHRASES = ("hallucinat", "reboot", "training data", "as an ai", "i am an ai")


def weighted_total(draft):
    """Add up one draft's rubric marks, each multiplied by its weight."""
    tally = 0
    for criterion, weight in WEIGHTS.items():
        mark = draft["marks"][criterion]
        if not 0 <= mark <= 5:
            raise ValueError(f"mark out of range for {criterion}: {mark!r}")
        tally += weight * mark
    return tally


def screen_line(line):
    """Reject any line the bounty gate would reject, with a reason."""
    stripped = line.strip()
    if line != stripped:
        raise ValueError("draft has leading or trailing whitespace")
    if not FLOOR <= len(stripped) <= CEILING:
        raise ValueError(f"draft is {len(stripped)} characters, gate allows {FLOOR}-{CEILING}")
    if "\n" in stripped or "\r" in stripped:
        raise ValueError("draft spans more than one line")
    if "  " in stripped:
        raise ValueError("draft contains a double space")
    lowered = stripped.lower()
    for phrase in WORN_PHRASES:
        if phrase in lowered:
            raise ValueError(f"draft leans on a worn joke: {phrase!r}")


def choose_line(drafts):
    """Score every screened draft; return the unique top scorer's line."""
    ranked = []
    for position, draft in enumerate(drafts):
        screen_line(draft["line"])
        ranked.append((weighted_total(draft), -len(draft["line"]), -position, draft["line"]))
    ranked.sort(reverse=True)
    top_total = ranked[0][0]
    leaders = [entry for entry in ranked if entry[0] == top_total]
    if len(leaders) != 1:
        raise ValueError(f"no unique winner: {len(leaders)} drafts tie at {top_total}")
    # A one-point win could flip on a single mis-keyed mark, so demand a
    # clear margin; a narrow win means the rubric needs reworking, not a
    # coin toss dressed up as a decision.
    margin = ranked[0][0] - ranked[1][0]
    if margin < 3:
        raise ValueError(f"winner's margin is only {margin} points; rubric too close to call")
    return ranked[0][3]


def audit_table(drafts):
    """Return the full ranking, best first, for a human to eyeball."""
    rows = []
    for draft in drafts:
        screen_line(draft["line"])
        rows.append((weighted_total(draft), len(draft["line"]), draft["line"]))
    rows.sort(key=lambda row: (-row[0], row[1]))
    lines = ["rank  total  chars  line"]
    for place, (total, size, line) in enumerate(rows, start=1):
        lines.append(f"{place:>4}  {total:>5}  {size:>5}  {line}")
    return "\n".join(lines) + "\n"


def write_entry(line, target):
    """Write the line as UTF-8 bytes with no trailing newline, then verify."""
    payload = line.encode("utf-8")
    destination = Path(target)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    reread = destination.read_bytes()
    if reread != payload:
        raise ValueError("entry file does not match the chosen line")
    digest = hashlib.sha256(reread).hexdigest()
    return digest


def run(argv=None):
    """Pick the winning confession and write it to the entry file."""
    parser = argparse.ArgumentParser(description="Write the winning one-line AI agent confession.")
    parser.add_argument("--out", default=DEFAULT_TARGET, help="where to write entry.txt")
    parser.add_argument("--audit", action="store_true", help="print the full draft ranking to stderr")
    options = parser.parse_args(argv)
    if options.audit:
        sys.stderr.write(audit_table(DRAFTS))
    confession = choose_line(DRAFTS)
    digest = write_entry(confession, options.out)
    sys.stdout.write(confession + "\n")
    sys.stdout.write(f"sha256: {digest}\n")
    return 0


if __name__.endswith("__main__"):
    raise SystemExit(run())
