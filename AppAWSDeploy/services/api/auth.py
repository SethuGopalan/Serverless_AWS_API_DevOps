import jwt
import requests
from jwt import PyJWKClient
from nitric.context import HttpContext



# Set your region and user pool ID
REGION = "us-east-1"
USER_POOL_ID = "us-east-1_sZHfsp1Q"
JWKS_URL = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"

def verify_token(ctx: HttpContext):
    auth_header = ctx.req.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise Exception("Missing or invalid Authorization header")

    token = auth_header.split(" ")[1]

    try:
        jwks_client = PyJWKClient(JWKS_URL)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        decoded = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=None,  # Optional: set your app client ID here
            issuer=f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}",
        )
        return decoded  # Optional: you can return user info from token
    except Exception as e:
        raise Exception(f"Token validation failed: {str(e)}")
