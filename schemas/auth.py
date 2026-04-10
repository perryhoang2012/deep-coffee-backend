from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    username: str
    password: str
    grant_type: str = ""
    scope: str = ""
    client_id: str = ""
    client_secret: str = ""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "admin",
                "password": "admin",
                "grant_type": "",
                "scope": "",
                "client_id": "",
                "client_secret": "",
            }
        }
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
