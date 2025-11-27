import argparse
import sys
import secrets
import string
import math
from typing import Iterable

SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>?/"

def pool_from_flags(use_upper:bool,use_lower:bool, use_digits:bool, use_symbols:bool) -> str:
    pool = ''
    if use_upper:
        pool += string.ascii_uppercase
    if use_lower:
        pool += string.ascii_lowercase
    if use_digits:
        pool += string.digits
    if use_symbols:
        pool += SYMBOLS
    return pool

def generate_password(length: int = 16, pool: str | None = None) -> str:
    if length <= 0:
        raise ValueError('length must be a positive integer')
    if pool is None:
        pool = pool_from_flags(use_upper=True, use_lower=True, use_digits=True, use_symbols=True)
    if not pool:
        raise ValueError('empty character pool')

    return ''.join(secrets.choice(pool) for _ in range(length))

def estimate_entropy_bits(length: int, pool_size: int) -> float:
    return length * math.log(pool_size)

def ensure_policy(password: str, require:Iterable[str]) -> bool:
    """Check that `password` contains at least one char from each pattern in `require` (each pattern is a string of allowed chars)."""
    for chars in require:
        if not any(c in chars for c in password):
            return False
    return True

#print(generate_password(length=14))
POLICIES = {
    'nist': {
        'min_length': 12,
        'require': ["abcdefghijklmnopqrstuvwxyz",
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                    "0123456789"]
    },
    'strict': {
        'min_length': 14,
        'require': ["abcdefghijklmnopqrstuvwxyz",
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                    "0123456789",
                    SYMBOLS]
    }
}

def parse_args():
    parser = argparse.ArgumentParser(description='Corporate password generator with policy enforcement')
    parser.add_argument('-l','--length', type=int, default=16, help='length of password')
    parser.add_argument('-c','--count', type=int, default=1, help='number of passwords to generate')
    parser.add_argument('--no-upper', dest='use_upper', action='store_true', help="Use upper case letters")
    parser.add_argument('--no-lower', dest='use_lower', action='store_true', help="Use lower case letters")
    parser.add_argument('--no-digits', dest='use_digits', action='store_true', help="Requires digits as well ")
    parser.add_argument('--no-symbols', dest='use_symbols', action='store_true', help="Symbols too")
    parser.add_argument('--policy', choices=list(POLICIES.keys()), default='strict', help="Policy to use")
    parser.add_argument('--save', type=str, default=None, help="Save generated password")
    parser.add_argument('--copy', action='store_true', help="Copy generated password")
    return parser.parse_args()

def main():
    args = parse_args()
    policy = POLICIES[args.policy]

    if args.length < policy['min_length']:
        print('Minimum password length must be at least {}'.format(policy['min_length']))

    pool = pool_from_flags(not args.use_upper, not args.use_lower, not args.use_digits, not args.use_symbols)

    if not pool:
        print('No pool specified', file=sys.stderr)
        sys.exit(2)

    generated = []
    for _ in range(args.count):
        # naive loop: keep generating until policy satisfied (rare re-rolls only)
        for _ in range(100):
            pw = generate_password(args.length, pool)
            if ensure_policy(pw, policy.get('require', [])):
                generated.append(pw)
                print(pw)
                break
        else:
            print("Failed to generate password after 100 tries", file=sys.stderr)

    if args.copy and generated:
        try:
            import pyperclip
            pyperclip.copy(generated[-1])
            print('[copied last password to clipboard]')
        except Exception:
            print('[failed to copy last password to clipboard. pip install pyperclip]', file=sys.stderr)

    if args.save and generated:
        with open(args.save, 'a', encoding='utf-8') as f:
            for pw in generated:
                f.write(pw + '\n')
        print(f"[saved {len(generated)} passwords to {args.save}]")

if __name__ == '__main__':
    main()