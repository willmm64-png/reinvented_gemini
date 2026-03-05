from __future__ import annotations

import keyring

SERVICE = "GeminiDesktop"
USERNAME = "gemini_api_key"


def get_api_key() -> str | None:
    return keyring.get_password(SERVICE, USERNAME)


def set_api_key(value: str) -> None:
    keyring.set_password(SERVICE, USERNAME, value)


def delete_api_key() -> None:
    try:
        keyring.delete_password(SERVICE, USERNAME)
    except keyring.errors.PasswordDeleteError:
        pass
