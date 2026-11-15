"""Configure a keyless UI profile and the org's default native launch model.

Run inside Enterprise 1.92.0 after configuring the gateway/catalog and member keys.
The existing admin settings validator preserves other agent configuration. Member
settings overrides are left untouched. No customer key is read or written here.

  docker compose cp cli/bootstrap_default_profile.py app:/tmp/bootstrap_default_profile.py
  docker compose exec -e PYTHONPATH=/app app python /tmp/bootstrap_default_profile.py \
      --org <org-uuid> --alias <catalog-alias> --profile-name <name>
"""

import argparse
import asyncio
import json
from uuid import UUID

from openhands.app_server.settings.llm_profiles import LLMProfiles
from openhands.sdk.llm import LLM
from openhands.sdk.settings import OpenHandsAgentSettings
from sqlalchemy import select

from server.customer_gateway.config import get_settings
from storage.customer_gateway import CustomerGatewayOrgConfig
from storage.database import a_session_maker
from storage.org import Org
from storage.org_store import OrgStore


async def bootstrap(org_id: UUID, alias: str, profile_name: str) -> None:
    settings = get_settings()
    if settings is None:
        raise SystemExit('Enable and configure the customer gateway first')

    async with a_session_maker() as session:
        org = (
            await session.execute(select(Org).where(Org.id == org_id).with_for_update())
        ).scalar_one_or_none()
        if org is None:
            raise SystemExit('Organization not found')
        gateway = await session.get(CustomerGatewayOrgConfig, org_id)
        if gateway is None or not gateway.enabled or alias not in gateway.profile['models']:
            raise SystemExit('Alias is not in this organization’s enabled gateway catalog')
        if not isinstance(OrgStore.get_agent_settings_from_org(org), OpenHandsAgentSettings):
            raise SystemExit('This bootstrap supports native OpenHands agents only')

        # Match the shape used by the relay binder so the existing UI can identify
        # the selected profile. All credential fields remain unset.
        llm = LLM(model=f'openai/{alias}', base_url=settings.relay_url, api_key=None)
        profiles = LLMProfiles.model_validate(org.llm_profiles or {})
        profiles.profiles[profile_name] = llm
        profiles.active = profile_name

        # Native API launches without llm_profile use agent_settings, not the
        # active picker profile. Use the same three-argument validator as the
        # existing OrgStore admin update path; keep member overrides intact.
        agent_settings = OrgStore._merge_and_validate_settings(
            org.agent_settings,
            {'llm': llm.model_dump(mode='json', context={'expose_secrets': True})},
            OpenHandsAgentSettings,
        )
        org.agent_settings = agent_settings.model_dump(mode='json', exclude_unset=True)
        org.llm_profiles = profiles.model_dump(mode='json', context={'expose_secrets': True})
        await session.commit()
    print(json.dumps({'profile': profile_name, 'model': llm.model, 'org_default_updated': True}))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--org', required=True, type=UUID)
    parser.add_argument('--alias', required=True, help='Alias from the configured gateway catalog')
    parser.add_argument('--profile-name', default='customer-gateway-default')
    args = parser.parse_args()
    asyncio.run(bootstrap(args.org, args.alias, args.profile_name))


if __name__ == '__main__':
    main()
