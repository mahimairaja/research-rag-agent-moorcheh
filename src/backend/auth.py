import os
import secrets
import time
from threading import Lock
from typing import Dict, Optional
from urllib.parse import urlencode

import jwt
import requests
import streamlit as st


class _StateStore:
    def __init__(self):
        self._states: dict[str, float] = {}
        self._lock = Lock()

    def add(self, state: str):
        with self._lock:
            self._states[state] = time.time()

    def consume(self, state: str, ttl_seconds: int = 600) -> bool:
        now = time.time()
        with self._lock:
            expired = [key for key, ts in self._states.items() if now - ts > ttl_seconds]
            for key in expired:
                self._states.pop(key, None)
            return self._states.pop(state, None) is not None


_STATE_STORE = _StateStore()


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

    def is_configured(self) -> bool:
        return self.oauth_available

    def generate_authorization_url(self, redirect_uri: str) -> tuple[str, str]:
        state = secrets.token_urlsafe(32)
        _STATE_STORE.add(state)

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
        if not _STATE_STORE.consume(state):
            st.error("Invalid OAuth state. Please try logging in again.")
            return None

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
