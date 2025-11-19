import hashlib
import hmac
import os
import secrets
from typing import Dict, Optional
from urllib.parse import urlencode

import jwt
import requests
import streamlit as st


class OAuthHandler:
    def __init__(self):
        self.client_id = os.getenv("OAUTH_CLIENT_ID")
        self.client_secret = os.getenv("OAUTH_CLIENT_SECRET")
        self.openid_provider_url = os.getenv(
            "OPENID_PROVIDER_URL", "https://huggingface.co"
        )
        self.space_host = os.getenv("SPACE_HOST", "")

        self.oauth_available = bool(self.client_id and self.client_secret)

        self.authorize_url = f"{self.openid_provider_url}/oauth/authorize"
        self.token_url = f"{self.openid_provider_url}/oauth/token"
        state_secret = (
            os.getenv("OAUTH_STATE_SECRET") or self.client_secret or "state-fallback-secret"
        )
        self._state_secret = state_secret.encode("utf-8")
        self.enforce_state = (
            os.getenv("ENFORCE_OAUTH_STATE", "false").lower() not in ("0", "false", "no")
        )

    def is_configured(self) -> bool:
        return self.oauth_available

    def _generate_state(self) -> str:
        nonce = secrets.token_urlsafe(16)
        signature = hmac.new(
            self._state_secret,
            nonce.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return f"{nonce}.{signature}"

    def _validate_state(self, state: str) -> bool:
        if not state or "." not in state:
            return False
        nonce, provided_signature = state.rsplit(".", 1)
        expected_signature = hmac.new(
            self._state_secret,
            nonce.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(provided_signature, expected_signature)

    def generate_authorization_url(self, redirect_uri: str) -> tuple[str, str]:
        state = self._generate_state()

        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": "openid profile",
            "response_type": "code",
            "state": state,
        }

        query_string = urlencode(params)
        auth_url = f"{self.authorize_url}?{query_string}"

        return auth_url, state

    def handle_callback(
        self, code: str, state: str, redirect_uri: str
    ) -> Optional[Dict]:
        if not self._validate_state(state):
            if self.enforce_state:
                st.error("Invalid OAuth state. Please try logging in again.")
                return None
            st.warning(
                "Unexpected OAuth state returned by the provider; continuing login for now."
            )

        try:
            token_data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }

            response = requests.post(self.token_url, data=token_data, timeout=10)
            response.raise_for_status()
            tokens = response.json()

            id_token = tokens.get("id_token")
            if not id_token:
                st.error("No ID token received from OAuth provider.")
                return None

            decoded_token = jwt.decode(
                id_token,
                options={
                    "verify_signature": False
                },
            )

            user_id = decoded_token.get("sub") or decoded_token.get(
                "preferred_username"
            )
            username = (
                decoded_token.get("preferred_username")
                or decoded_token.get("name")
                or user_id
            )

            if not user_id:
                st.error("Could not extract user ID from OAuth token.")
                return None

            user_info = {
                "user_id": user_id,
                "username": username,
                "id_token": id_token,
                "access_token": tokens.get("access_token"),
            }

            st.session_state.user_info = user_info
            st.session_state.authenticated = True

            return user_info

        except requests.exceptions.RequestException as e:
            st.error(f"Error exchanging OAuth code: {str(e)}")
            return None
        except jwt.DecodeError as e:
            st.error(f"Error decoding ID token: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Unexpected error during OAuth callback: {str(e)}")
            return None

    def get_current_user(self) -> Optional[Dict]:
        if st.session_state.get("authenticated"):
            return st.session_state.get("user_info")
        return None

    def get_user_id(self) -> Optional[str]:
        user_info = self.get_current_user()
        if user_info:
            return user_info.get("user_id")
        return None

    def logout(self):
        if "user_info" in st.session_state:
            del st.session_state.user_info
        if "authenticated" in st.session_state:
            del st.session_state.authenticated


def get_current_user_id() -> Optional[str]:
    handler = OAuthHandler()
    return handler.get_user_id()
