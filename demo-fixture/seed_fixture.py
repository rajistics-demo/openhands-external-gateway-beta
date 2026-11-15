"""Operator RESTORE of the two existing, approved member fixtures into the STAGING HARNESS
fresh DB. This restores existing identities; it does not provision. Run inside the app pod
before the first native login, with a private JSON document on stdin (never argv, never in
the chart):

  {"provider": {"id": <int, existing fixture provider id>, "title": "...", "is_idp": true,
                "enabled": true, "details": {<OAuthProviderDetails of the NEW client:
                provider_type, client_id, client_secret, authorization_url, token_url,
                userinfo_url, scopes, attribute_mapping>}},
   "org":   {"id": "<shared fixture org UUID>", "name": "..."},
   "users": [{"user_id": "<canonical UUID>", "subject": "<IdP sub>", "email": "...",
              "accepted_tos": "<ISO timestamp or null>", "role": "member"}, ...]}

ORM constructors only, in one transaction:
  * ``auth_providers`` keeps its integer id; ``details`` (new client secret) is encrypted by
    the model with this release's fresh JWT secret. Registration and email matching are off.
  * ``org`` keeps its UUID, with clean defaults (no model profiles).
  * ``user`` rows keep their canonical UUIDs: ``role_id=None`` (never super-admin),
    ``account_type='human'``, ``current_org_id`` = the shared org, ``accepted_tos`` copied.
    No ``UserStore.create_user``: no personal orgs, no admin bootstrap, no managed-LLM calls.
  * ``org_member`` gets the named org role and a fresh, unused, encrypted placeholder in the
    NOT NULL legacy key column. No old LLM keys, OAuth tokens or profile keys are copied.
  * ``auth_provider_users`` links ``(provider id, sub) -> canonical UUID``, so the native
    OAuth v2 callback (server/auth/provider_identity.py ``resolve_or_create_user``) resolves
    the existing user.
No invitations, no email. Refuses to run if any of the users already exists.
Personal customer keys are imported afterwards with ``python -m server.customer_gateway.cli``.
"""

import asyncio
import json
import secrets
import sys
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, text

from storage.auth_provider import AuthProvider
from storage.auth_provider_details import OAuthProviderDetails
from storage.auth_provider_user import AuthProviderUser
from storage.database import a_session_maker
from storage.org import Org
from storage.org_member import OrgMember
from storage.role import Role
from storage.user import ACCOUNT_TYPE_HUMAN, User


async def restore(doc: dict, session_maker=a_session_maker) -> None:
    p, o = doc['provider'], doc['org']
    org_id = UUID(o['id'])
    async with session_maker() as s:
        for u in doc['users']:
            if await s.get(User, UUID(u['user_id'])) is not None:
                raise SystemExit(f'user {u["user_id"]} already exists; restore is one-shot')
        provider = await s.get(AuthProvider, p['id'])
        if provider is None:
            provider = AuthProvider(id=p['id'])
            s.add(provider)
        provider.title = p['title']
        provider.is_idp = p.get('is_idp', True)
        provider.enabled = p.get('enabled', True)
        provider.allow_registration = False
        provider.allow_match_by_email = False
        provider.details = OAuthProviderDetails.model_validate(p['details'])
        if await s.get(Org, org_id) is None:
            # contact_name/contact_email are nullable at the DB layer (storage/org.py)
            # but OrgResponse (server/routes/org_models.py) declares them as plain,
            # required `str` fields with no default. An org created without them
            # serializes fine until something returns it through OrgResponse, which
            # then 500s on Pydantic validation (None is not a str) — this is how a
            # fresh fixture org broke the UI's workspace listing in root's diagnosis.
            # This is a gap in THIS fixture script, not a gateway/product bug; no
            # product/UI code changes are made for it. Override via doc['org'] if the
            # restored identity has real contact details to use instead.
            s.add(
                Org(
                    id=org_id,
                    name=o['name'],
                    contact_name=o.get('contact_name', 'Gateway Evaluation Operator'),
                    contact_email=o.get('contact_email', 'operator@example.com'),
                )
            )
        await s.flush()
        for u in doc['users']:
            uid = UUID(u['user_id'])
            role = (
                await s.execute(select(Role).where(Role.name == u.get('role', 'member')))
            ).scalar_one()
            tos = u.get('accepted_tos')
            s.add(
                User(
                    id=uid,
                    current_org_id=org_id,
                    role_id=None,
                    account_type=ACCOUNT_TYPE_HUMAN,
                    accepted_tos=datetime.fromisoformat(tos) if tos else None,
                    email=(u.get('email') or '').strip().lower() or None,
                )
            )
            await s.flush()
            member = OrgMember(org_id=org_id, user_id=uid, role_id=role.id, status='active')
            member.llm_api_key = f'customer-gateway-unused-{secrets.token_hex(16)}'
            s.add(member)
            s.add(
                AuthProviderUser(
                    oauth_provider_id=p['id'],
                    user_id=uid,
                    external_subject_id=u['subject'],
                    external_email=u.get('email'),
                )
            )
        if s.get_bind().dialect.name == 'postgresql':
            await s.execute(
                text(
                    "SELECT setval(pg_get_serial_sequence('auth_providers', 'id'),"
                    ' (SELECT max(id) FROM auth_providers))'
                )
            )
        await s.commit()


if __name__ == '__main__':
    doc = json.load(sys.stdin)
    asyncio.run(restore(doc))
    print(f'restored provider {doc["provider"]["id"]}, {len(doc["users"])} users, org {doc["org"]["id"]}')
