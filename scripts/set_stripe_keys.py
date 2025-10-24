"""Utility script to programmatically set Stripe keys into config/settings.py for local/dev use.

WARNING: This writes secrets into repository files. Do NOT commit these keys to version control.
Use this only in a secure development environment. For production prefer environment variables or a secrets manager.
"""
import sys
import re
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config' / 'settings.py'

def set_key(name, value):
    text = CONFIG_PATH.read_text()
    pattern = rf"^{name}\s*=.*$"
    replacement = f"{name} = '{value}'"
    if re.search(pattern, text, flags=re.MULTILINE):
        new_text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
    else:
        new_text = text + "\n" + replacement + "\n"
    CONFIG_PATH.write_text(new_text)
    print(f"Set {name} in {CONFIG_PATH}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python scripts/set_stripe_keys.py <STRIPE_SECRET_KEY> <STRIPE_WEBHOOK_SECRET>')
        sys.exit(1)
    secret_key = sys.argv[1]
    webhook = sys.argv[2]
    set_key('STRIPE_SECRET_KEY', secret_key)
    set_key('STRIPE_WEBHOOK_SECRET', webhook)
    print('Done. Restart the server to pick up changes.')