import argparse
import secrets
import string
from pass_corpo import generate_password, SYMBOLS

MASK_TOKEN_MAP = {
    '?l' : string.ascii_lowercase,
    '?u' : string.ascii_uppercase,
    '?d' : string.digits,
    '?s' : SYMBOLS,
}

def generate_from_mask(mask: str) -> str:
    out = []
    i = 0
    while i < len(mask):
        if mask[i] == '?' and i+1 < len(mask):
            tok = mask[i:i+2]
            chars = MASK_TOKEN_MAP.get(tok)
            if chars:
                out.append(secrets.choice(chars))
                i += 1
                continue
        #literal char
        out.append(mask[i])
        i += 1
    return ''.join(out)

def leet_variants(word: str):
    subs = {'a':'@','o':'0','i':'1','e':'3','s':'$','t':'7'}
    yield  word
    for k,v in subs.items():
        if k in word.lower():
            yield word.replace(k, v)
            yield word.replace(k.upper(), v)

def main():
    parser = argparse.ArgumentParser(description='Pentest generator')
    parser.add_argument('--mask', type=str, help='mask password')
    parser.add_argument('-c', '--count', type=int, default=10, help='number of passwords to generate')
    parser.add_argument('--word', type=str, help='base word to mixed')
    parser.add_argument('--mangle', action='store_true')
    parser.add_argument('--passphrase', action='store_true')
    parser.add_argument('--wordlist', type=str, help='wordlist file')
    args = parser.parse_args()

    # Mask Mode
    if args.mask:
        for _ in range(args.count):
            print(generate_from_mask(args.mask))
        return

    # Mangle Mode
    if args.word and args.mangle:
        for i, v in enumerate(leet_variants(args.word)):
            if i >= args.count:
                break
            # also add numeric suffixes
            print(v + str(secrets.randbelow(1000)))
        return

    # Passphrase Mode
    if args.passphrase:
        word = []
        if args.wordlist:
            with open(args.wordlist, encoding='utf-8') as f:
                words = [w.strip() for w in f if w.strip()]
        else:
            # small fallback
            words = ['correct', 'horse', 'battery', 'staple', 'alpha', 'bravo', 'charlie']

        for _ in range(args.count):
            parts = [secrets.choice(words) for _ in range(14)]
            print(' '.join(parts))
        return

    # fallback: random passwords
    for _ in range(args.count):
        print(generate_password(14))

if __name__ == '__main__':
    main()