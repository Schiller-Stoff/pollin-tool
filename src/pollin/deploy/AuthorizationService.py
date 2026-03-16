import logging
from urllib.parse import urljoin
from pyrilo.api.GamsApiClient import GamsApiClient  # <--- Changed from requests
from pyrilo.api.auth.LoginFormParser import LoginFormParser


class AuthorizationService:
    # 1. Inject the Client, not the Session
    def __init__(self, client: GamsApiClient):
        self.client = client

    def login(self, username: str = None, password: str = None) -> None:
        """
        Performs authentication using the shared GamsApiClient.
        """
        # 2. Use 'auth' endpoint. The client automatically prepends {host}/api/v1/
        # This replaces: login_url = f"{self.host}{PyriloStatics.AUTH_ENDPOINT}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Upgrade-Insecure-Requests': '1'
        }

        # 3. Use client.get()
        # We assume the API returns HTML here, but client.get returns the response object, so that's fine.
        response = self.client.get("auth", headers=headers)
        response.raise_for_status()

        # Parsing the keycloak form
        parser = LoginFormParser()
        parser.feed(response.text)

        if not parser.action:
            # If we can't find a form, we might already be logged in.
            logging.warning("No login form found. Assuming already authenticated or non-standard page.")
            return

        action_url = parser.action
        logging.debug("Redirecting to keycloak url: ", action_url)
        if not action_url.startswith('http'):
            # This creates an absolute URL
            action_url = urljoin(response.url, action_url)

        if not username or not password:
            raise ValueError("Authentication required...")

        payload = {'username': username, 'password': password, 'credentialId': ''}
        payload.update(parser.hidden_inputs)

        # 4. Use client.post() with the absolute URL (handled by our client upgrade)
        post_response = self.client.post(action_url, data=payload, headers=headers)

        # --- VALIDATION LOGIC START ---

        # Check 1: HTTP Error Codes (401/403)
        if post_response.status_code >= 400:
            raise PermissionError(f"Login failed with status {post_response.status_code}.")

        # Check 2: "error" in URL (Common Spring/Java pattern: /login?error)
        if "error" in post_response.url.lower():
            raise PermissionError("Login failed: Invalid credentials (server returned error param).")

        # Check 3: Did we land back on the login page?
        if 'type="password"' in post_response.text.lower():
            raise PermissionError("Login failed: Login form detected in response content.")

        # --- VALIDATION LOGIC END ---
        logging.info("Login successful (session cookie established).")

        # csrf token needs to be read out from cookie and then used via request header (that's the core idea of the protection against CSRF attacks)
        csrf_token = post_response.cookies.get('XSRF-TOKEN')

        if not csrf_token:
            raise PermissionError("Login failed: csrf token not found in gams-api response.")

        self.client.session.headers.update(
            {
                "X-XSRF-TOKEN": csrf_token
                # the jsession-id as being handled by the corresponding cookie
            }
        )