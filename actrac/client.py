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
import sys

import httpx

from actrac.api import ACTAPI
from actrac.constants import ACT_REST_API_BASE_URL
from actrac.errors import ACTRESTAPIError


class ACTClient:
    """ACTClient for interacting with ACT REST API."""

    def __init__(  # noqa: PLR0913
        self,
        api_key,
        https=False,
        base_url=None,
        cert=False,
        log_file=None,
        log_level="INFO",
        log_stdout=False,
    ):
        """Initialize the client.

        :param api_key: key for authentication.
        :param https: connect to ACT via HTTPS instead of OVPN.
        :param base_url: The base of the URL used for REST API requests.
        Tenant as a string.
        :param cert: Verify certificate. Default False.
        :param log_file: file to write log messages to as string.
        :param log_level: logging level as string.
        :param log_stdout: print log messages to standard out or not.
        """
        self.api_key = api_key
        self.token = None
        self.https = https
        self.base_url = base_url or ACT_REST_API_BASE_URL
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

    def get_access_token(self):
        """Authenticate to ACT for provided api key.

        :return: access token as string for success.
        """
        # Authenticate with ACT and return the token
        url = f"{self.base_url}/auth/login"
        # Form the headers and data for the request
        headers = {"content-type": "application/json"}
        data = {"api_key": self.api_key}
        # Send the request
        response = httpx.post(url, headers=headers, json=data, verify=self.cert).raise_for_status()
        # Get the token from the response or report an error
        token = response.json().get("token")
        if not token:
            err_str = f"Authentication failed. No token found: {response.json()}"
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
            base_url=self.base_url, headers=self.headers, timeout=timeout, verify=self.cert
        )

    def _validate_response(self, response):
        """Validate the response for given request.

        :param response: response from request
        :return: JSON decoded response data.
        """
        data = {}
        if response:
            if response.status_code != httpx.codes.OK:
                err_msg = f"Response for request {response.url} is not OK. {response.status_code}"
                self.log.error(err_msg)
            try:
                data = response.json()
            except Exception as exc:
                err_msg = f"Error decoding request {response.url} response data {response}"
                self.log.error(exc)
        else:
            self.log.error(f"Response for request {response.url} is None.")
        return data

    def get(self, url, params=None, timeout=30):
        """Make GET Request with provided parameters.

        :param url: ...
        :param params: ...
        :param timeout: configure timeout for get request.
        """
        if self.client:
            resp = self.client.get(url, params=params, timeout=timeout).raise_for_status()
            return self._validate_response(resp)

    def post(self, url, data=None, timeout=30):
        """Make POST Request with provided parameters.

        :param url: ...
        :param data: ...
        :param timeout: configure timeout for post request.
        """
        if self.client:
            json_data = json.dumps(data)
            resp = self.client.post(url, data=json_data, timeout=timeout).raise_for_status()
            return self._validate_response(resp)

    def patch(self, url, data=None, timeout=30):
        """Make PATCH Request with provided parameters.

        :param url: ...
        :param data: ...
        :param timeout: configure timeout for patch request.
        """
        if self.client:
            json_data = json.dumps(data)
            resp = self.client.patch(url, data=json_data, timeout=timeout).raise_for_status()
            return self._validate_response(resp)

    def delete(self, url, timeout=30):
        """Make DELETE Request with provided parameters.

        :param url: ...
        :param timeout: configure timeout for delete request.
        """
        if self.client:
            resp = self.client.delete(url, timeout=timeout).raise_for_status()
            return self._validate_response(resp)
