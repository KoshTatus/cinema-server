from datetime import timedelta
from dataclasses import dataclass

jwt_secret = "47f847a9ed6821557bbca7eeb533d9836763b9bd8e0a28364b664e5008e2d9e308cfd26e908267ab285d79aa9d2656079e2dfe28789b673c94b8a1f53539ab3f"

@dataclass
class JWTConfig:
    secret: str = jwt_secret
    algorithm: str = "HS256"
    access_token_ttl: timedelta = timedelta(hours=1)