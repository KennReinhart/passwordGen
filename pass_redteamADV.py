#!/usr/bin/env python3
import argparse
import json
import secrets
import string
import hashlib
import random
import itertools
import os


# -------------------------------
# MASK ENGINE
# -------------------------------
SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>/?"

MASK_TOKEN_MAP = {
    "?l": string.ascii_lowercase,
    "?u": string.ascii_uppercase,
    "?d": string.digits,
    "?s": SYMBOLS,
}

def generate_mask(mask: str) -> str:
    """Generate one password from a mask."""
    out = []
    i = 0
    while i < len(mask):
        if mask[i] == "?" and i + 1 < len(mask):
            tok = mask[i:i+2]
            chars = MASK_TOKEN_MAP.get(tok)
            if chars:
                out.append(secrets.choice(chars))
                i += 2
                continue
        out.append(mask[i])
        i += 1
    return ''.join(out)


# -------------------------------
# SIMPLE ONE-SHOT MANGLE ENGINE
# -------------------------------
LEET_MAP = {
    "a": "@",
    "e": "3",
    "i": "1",
    "o": "0",
    "s": "$",
    "t": "7",
}

def leet(word: str) -> str:
    out = ""
    for ch in word:
        low = ch.lower()
        out += LEET_MAP.get(low, ch)
    return out

# -------------------------------
# CASE VARIANTS (AUTO)
# -------------------------------
def case_variants(word: str):
    return [
        word.lower(),
        word.upper(),
        word.capitalize()
    ]

# -------------------------------
# HASHING FOR OSINT / CORRELATION
# -------------------------------
def compute_hashes(word: str):
    return {
        "md5": hashlib.md5(word.encode()).hexdigest(),
        "sha1": hashlib.sha1(word.encode()).hexdigest(),
        "sha256": hashlib.sha256(word.encode()).hexdigest()
    }

# -------------------------------
# PROFILE SYSTEM
# -------------------------------
def save_profile(path, name, nick, dob):
    with open(path, "w") as f:
        json.dump({"name": name, "nick": nick, "dob": dob}, f, indent=2)

def load_profile(path):
    with open(path) as f:
        return json.load(f)

# -------------------------------
# COMBINATION BUILDER
# -------------------------------
def build_combos(*words):
    """Return the 4 standard combos."""
    # Generate permutations of words
    combos = set()
    for r in range(1, len(words) + 1):
        for perm in itertools.permutations(words, r):
            combos.add("".join(perm))

    # Apply random case variants
    final = set()
    for c in combos:
        for variant in case_variants(c):
            final.add(variant)

    # Shuffle output
    final = list(final)
    random.shuffle(final)
    return final

# -------------------------------
# MAIN
# -------------------------------
def main():
    parser = argparse.ArgumentParser(description="Advanced Red-Team Password Generator")

    # profile load/save
    parser.add_argument("--save-profile", type=str, help="Save inputs to JSON profile")
    parser.add_argument("--load-profile", type=str, help="Load profile JSON file")

    # user data
    parser.add_argument("--name", type=str, help="Full name")
    parser.add_argument("--email", type=str, help="Email address")
    parser.add_argument("--dob", type=str, help="Date of Birth")
    parser.add_argument("--mob", type=str, help="Month of birth")
    parser.add_argument("--yob", type=str, help="Year of birth")

    # mutate options
    parser.add_argument("--leet", action="store_true")
    parser.add_argument("--reverse", action="store_true")

    # mask mode
    parser.add_argument("--mask", type=str, help="Mask pattern like ?l?l?d?d?s")
    parser.add_argument("--count", type=int, default=1, help="Number of results")

    # output
    parser.add_argument("--output", type=str, help="Save final list to a file")
    parser.add_argument("--hashes", action="store_true", help="Also print MD5/SHA1/SHA256")

    args = parser.parse_args()

    # LOAD PROFILE
    if args.load_profile:
        p = load_profile(args.load_profile)
        args.name = p.get("name")
        args.email = p.get("email")
        args.dob = p.get("dob")
        args.mob = p.get("mob")
        args.yob = p.get("yob")

    # MASK MODE
    if args.mask:
        print("\nGenerated passwords:")
        for _ in range(args.count):
            pw = generate_mask(args.mask)
            print("  " + pw)
            if args.hashes:
                h = compute_hashes(pw)
                print("    MD5:    " + h["md5"])
                print("    SHA1:   " + h["sha1"])
                print("    SHA256: " + h["sha256"])
        return

    # INTERACTIVE INPUT
    if not args.name:
        args.name = input("Full Name: ").strip()

    if not args.email:
        args.email = input("Email: ").strip()

    if not args.dob:
        args.dob = input("Date of Birth): ").strip()

    if not args.mob:
        args.mob = input("Month of Birth): ").strip()

    if not args.yob:
        args.yob = input("Year of Birth): ").strip()

    name = args.name.replace(" ", "")
    email = args.email.replace(" ", "")
    dob = args.dob.replace(" ", "")
    mob = args.mob.replace(" ", "")
    yob = args.yob.replace(" ", "")

    # SAVE PROFILE IF ASKED
    if args.save_profile:
        save_profile(args.save_profile, name, email, yob)

    # Build combinations
    combos = build_combos(name, email, dob, mob, yob)

    # Apply one-shot mangling
    final = []
    for c in combos:
        variants = case_variants(c) # lower, upper, tittle, original

        for v in variants:
            w = v
            if args.leet:
                w = leet(w)
            if args.reverse:
                w = w[::-1]

            final.append(w)

    # Remove duplicates
    final = list(dict.fromkeys(final))

    # Output
    print("\nGenerated passwords:")
    for w in final:
        print("  " + w)
        if args.hashes:
            h = compute_hashes(w)
            print("    MD5:    " + h["md5"])
            print("    SHA1:   " + h["sha1"])
            print("    SHA256: " + h["sha256"])

    # Save file
    if args.output:
        with open(args.output, "w") as f:
            for w in final:
                f.write(w + "\n")
        print(f"\nSaved to {args.output}")

if __name__ == "__main__":
    main()

#in terminal
# python pass_redteamADV.py --name kenreinhart --email reinhartplaysgames@gmail.com --dob 1990 --leet --hashes
