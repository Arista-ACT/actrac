#
# Copyright (c) 2024, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Arista Networks nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# 'AS IS' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

"""Client for interacting with the ACT Websocket API."""

import json
import logging
import re
import sys

import httpx

from actrac.api import ACTAPI
from actrac.constants import ACT_REST_API_PATH
from actrac.errors import ACTRESTAPIError


class ACTClient:
    """ACTClient for interacting with ACT REST API."""

    def __init__(  # noqa: PLR0913
        self,
        api_key,
        base_url,
        cert=False,
        log_file=None,
        log_level="INFO",
        log_stdout=False,
    ):
        """Initialize the client.

        :param api_key: key for authentication.
        :param base_url: The base of the URL used for REST API requests.
            Example: https://lab.act.arista.com or lab.act.arista.com
        :param cert: Verify certificate. Default False.
        :param log_file: file to write log messages to as string.
        :param log_level: logging level as string.
        :param log_stdout: print log messages to standard out or not.
        """
        self.api_key = api_key
        self.token = None
        # ^               : Start of the string
        # (https://)?     : Capturing group 1 for optional 'https://'
        # (?:[a-zA-Z0-9-]+\.)+ : Non-capturing group for REQUIRED tenant ID portion.
        #                        Matches alphanumeric/hyphen followed by a MANDATORY dot.
        # key\.blah\.com  : Literal match for the required suffix.
        # $               : End of string (ensures no path exists)
        valid_url_pattern = re.compile(r"^(https://)?(?:[a-zA-Z0-9-]+\.)+act\.arista\.com$")
        match = valid_url_pattern.match(base_url)
        if not match:
            err_str = (
                f"Invalid base_url: {base_url}. Use format "
                "https://<tenant identifier>.act.arista.com or <tenant identifier>.act.arista.com"
            )
            raise ACTRESTAPIError(err_str)
        # Add https:// if not already in base_url
        if not match.group(1):
            base_url = f"https://{base_url}"
        self.base_url = base_url
        self.full_url = f"{self.base_url}{ACT_REST_API_PATH}"
        self.cert = cert
        self.log = logging.getLogger("actrac")
        self.configure_log(log_file, log_level, log_stdout)
        self.client = None
        self.api = ACTAPI(self)

    def configure_log(self, log_file=None, log_level="INFO", log_stdout=False):
        """Configure logging for ACT REST API client.

        :param log_file: file to log to.
        :param log_level: level of log messages to write.
        :param log_stdout: log to standard out or not.
        :return: None
        """
        log_level = log_level.upper()
        if log_level not in ["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            log_level = "INFO"
        self.log.setLevel(getattr(logging, log_level))
        if log_file:
            self.log.addHandler(logging.FileHandler(log_file))
        if log_stdout:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(getattr(logging, log_level))
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.log.addHandler(handler)
        if not log_file and not log_stdout:
            self.log.addHandler(logging.NullHandler())

    def _validate_response(self, response):
        """Validate the response for given request.

        :param response: response from request
        :return: JSON decoded response data.
        """
        data = {}
        if response:
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == httpx.codes.NOT_FOUND:
                    self.log.warning("No data found for request %s", exc.request.url)
                    return data
                else:
                    raise

            if response.status_code != httpx.codes.OK:
                err_msg = f"Response for request {response.url} is not OK. {response.status_code}"
                self.log.error(err_msg)
                return data

            try:
                data = response.json()
            except Exception as exc:
                err_msg = f"Error decoding request {response.url} response data {response}"
                self.log.error(exc)
        else:
            self.log.warning("Response is None.")
        return data

    def get_access_token(self):
        """Authenticate to ACT for provided api key.

        :return: access token as string for success.
        """
        # Authenticate with ACT and return the token
        url = f"{self.full_url}/auth/login"
        # Form the headers and data for the request
        headers = {"content-type": "application/json"}
        data = {"api_key": self.api_key}
        # Send the request
        resp = httpx.post(url, headers=headers, json=data, verify=self.cert)
        resp_data = self._validate_response(resp)
        # Get the token from the response or report an error
        token = resp_data.get("token")
        if not token:
            err_str = f"Authentication failed. No token found: {resp_data}"
            self.log.error(err_str)
            raise ACTRESTAPIError(err_str)
        return token

    def connect(self, timeout=30):
        """Create REST API Client connection to ACT.

        :param cert: use certificate validation or not.
        :param timeout: request timeout for client.
        :return: None
        """
        self.token = self.get_access_token()
        self.headers = {"content-type": "application/json", "Authorization": f"Bearer {self.token}"}
        self.client = httpx.Client(
            base_url=self.full_url, headers=self.headers, timeout=timeout, verify=self.cert
        )

    def disconnect(self, timeout=30):
        """Disconnect the current connection to ACT via logout.

        :param timeout: request timeout for client.
        :return: None
        """
        self.post("/auth/logout", timeout=timeout)

    def get(self, url, params=None, timeout=30):
        """Make GET Request with provided parameters.

        :param url: ...
        :param params: ...
        :param timeout: configure timeout for get request.
        """
        if self.client:
            resp = self.client.get(url, params=params, timeout=timeout)
            return self._validate_response(resp)

    def post(self, url, data=None, timeout=30):
        """Make POST Request with provided parameters.

        :param url: ...
        :param data: ...
        :param timeout: configure timeout for post request.
        """
        if self.client:
            json_data = json.dumps(data)
            resp = self.client.post(url, data=json_data, timeout=timeout)
            return self._validate_response(resp)

    def patch(self, url, data=None, timeout=30):
        """Make PATCH Request with provided parameters.

        :param url: ...
        :param data: ...
        :param timeout: configure timeout for patch request.
        """
        if self.client:
            json_data = json.dumps(data)
            resp = self.client.patch(url, data=json_data, timeout=timeout)
            return self._validate_response(resp)

    def delete(self, url, timeout=30):
        """Make DELETE Request with provided parameters.

        :param url: ...
        :param timeout: configure timeout for delete request.
        """
        if self.client:
            resp = self.client.delete(url, timeout=timeout)
            return self._validate_response(resp)
