import random
import itertools
import hashlib

def random_case_variants(word):
    return {
        word.lower(),
        word.upper(),
        word.capitalize(),
    }

def combine_randomized(*words):
    """Return a shuffled random combination of the given words."""
    # Remove None or empty strings
    words = [w for w in words if w]

    # Generate permutations of words
    combos = set()
    for r in range(1, len(words) + 1):
        for perm in itertools.permutations(words, r):
            combos.add("".join(perm))

    # Apply random case variants
    final = set()
    for c in combos:
        for variant in random_case_variants(c):
            final.add(variant)

    # Shuffle output
    final = list(final)
    random.shuffle(final)
    return final

# Example harmless usage:
name = "andi"
dob = "12031995"
nick = "ace"

print("Randomized combinations:")
for c in combine_randomized(name, dob, nick)[:20]:  # just show 20 examples
    print(c)

# Optional: Hashing demonstration (neutral)
def hash_all(s):
    return {
        "md5": hashlib.md5(s.encode()).hexdigest(),
        "sha1": hashlib.sha1(s.encode()).hexdigest(),
        "sha256": hashlib.sha256(s.encode()).hexdigest()
    }

example = "andi12031995"
print("\nHash examples:")
print(hash_all(example))
