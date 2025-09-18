from fastapi.security import OAuth2AuthorizationCodeBearer
from fief_client import FiefAsync
from fief_client.integrations.fastapi import FiefAuth

from abdullateef_api.settings import settings

fief = FiefAsync(
    settings.fief_base_url,
    settings.fief_client_id,
    settings.fief_client_secret,
)

scheme = OAuth2AuthorizationCodeBearer(
    f"{settings.fief_base_url}/authorize",
    f"{settings.fief_base_url}/api/token",
    scopes={"openid": "openid"},
    auto_error=False,
)

auth = FiefAuth(fief, scheme)
