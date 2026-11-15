"""TEST-ONLY customer LiteLLM fixture tool (R3 tools/seed_litellm.py recipe). Runs only in the
fixture tools pod, which alone holds the fixture master key; the product app never does.

The central budget belongs to the customer USER, not to a key: create the user once with
``max_budget`` and its model permissions, then issue any number of keys owned by that same
user_id (initial, rotated, a second app's). New keys therefore cannot reset the user's spend.

  python fixture_seed_key.py user --user cust-susan-<n> --models deepseek-chat,claude-sonnet --budget 1.0
  python fixture_seed_key.py key  --user cust-susan-<n> --models deepseek-chat,claude-sonnet --alias oh-susan-<n>

``user`` prints nothing secret. If the user already exists it is left unchanged (no budget
reset). ``key`` prints one key on stdout, for piping straight into the product CLI ``set-key``.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def call(path: str, body: dict) -> tuple[int, dict | str]:
    req = urllib.request.Request(
        os.environ['LITELLM_URL'].rstrip('/') + path,
        data=json.dumps(body).encode(),
        headers={
            'Authorization': f'Bearer {os.environ["LITELLM_MASTER_KEY"]}',
            'Content-Type': 'application/json',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors='replace')


p = argparse.ArgumentParser()
sub = p.add_subparsers(dest='cmd', required=True)
u = sub.add_parser('user')
u.add_argument('--user', required=True)
u.add_argument('--models', required=True)
u.add_argument('--budget', type=float, required=True)
k = sub.add_parser('key')
k.add_argument('--user', required=True)
k.add_argument('--models', required=True)
k.add_argument('--alias', required=True)
a = p.parse_args()
models = a.models.split(',')

if a.cmd == 'user':
    status, body = call(
        '/user/new',
        {
            'user_id': a.user,
            'max_budget': a.budget,
            'models': models,
            'auto_create_key': False,
        },
    )
    if status >= 400:
        if 'already' not in str(body).lower():
            sys.exit(f'/user/new failed: {status}')
        print(f'user {a.user} exists; budget unchanged', file=sys.stderr)
    else:
        print(f'user {a.user} created, max_budget={a.budget}', file=sys.stderr)
else:
    status, body = call(
        '/key/generate', {'user_id': a.user, 'key_alias': a.alias, 'models': models}
    )
    if status >= 400 or not isinstance(body, dict):
        sys.exit(f'/key/generate failed: {status}')
    sys.stdout.write(body['key'] + '\n')
