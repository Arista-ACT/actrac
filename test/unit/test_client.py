#
# Copyright (c) 2022, Arista Networks, Inc.
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

import logging
import os

import httpx
import pytest

from actrac.client import ACTClient
from actrac.constants import ACT_REST_API_PATH
from actrac.errors import ACTRESTAPIError

TEST_ACT_REST_API_BASE_URL = "https://lab.act.arista.com"


class MockHttpxResponseValid:
    def __init__(self):
        self.url = "MOCKURL"
        self.status_code = httpx.codes.OK

    @staticmethod
    def raise_for_status():
        return None

    @staticmethod
    def json():
        return {"data": "data"}


class MockHttpxResponseNotOK:
    def __init__(self):
        self.url = "MOCKURL"
        self.status_code = httpx.codes.NOT_FOUND

    @staticmethod
    def raise_for_status():
        return None

    @staticmethod
    def json():
        return {"data": "data"}


class MockHttpxResponseInvalidJSON:
    def __init__(self):
        self.url = "MOCKURL"
        self.status_code = httpx.codes.OK

    @staticmethod
    def raise_for_status():
        return None

    @staticmethod
    def json():
        raise Exception("MOCK JSON DECODE ERROR")


class MockHttpxResponseRaiseUncaughtException:
    def __init__(self):
        self.url = "MOCKURL"
        self.status_code = httpx.codes.OK

    @staticmethod
    def raise_for_status():
        raise Exception("UNCAUGHT EXCEPTION")

    @staticmethod
    def json():
        return {"data": "data"}


class MockHttpxGoodTokenResponse:
    def __init__(self):
        self.url = "MOCKURL"
        self.status_code = httpx.codes.OK

    @staticmethod
    def raise_for_status():
        return None

    @staticmethod
    def json():
        return {"token": "mocktoken"}


class MockHttpxNoTokenResponse:
    def __init__(self):
        self.url = "MOCKURL"
        self.status_code = httpx.codes.OK

    @staticmethod
    def raise_for_status():
        return None

    @staticmethod
    def json():
        return {"token": None}


class TestACTClient:
    """TestACTClient."""

    def test_client_init(self):
        clnt = ACTClient(api_key="TEST", base_url=TEST_ACT_REST_API_BASE_URL)
        assert clnt.api_key == "TEST"
        assert clnt.token is None
        assert clnt.base_url == TEST_ACT_REST_API_BASE_URL
        assert clnt.full_url == f"{TEST_ACT_REST_API_BASE_URL}{ACT_REST_API_PATH}"
        assert clnt.cert is False
        assert clnt.client is None
        assert clnt.log.level == logging.INFO

    def test_client_init_base_url_has_no_https(self):
        clnt = ACTClient(api_key="TEST", base_url="lab.act.arista.com")
        assert clnt.api_key == "TEST"
        assert clnt.token is None
        assert clnt.base_url == TEST_ACT_REST_API_BASE_URL
        assert clnt.full_url == f"{TEST_ACT_REST_API_BASE_URL}{ACT_REST_API_PATH}"
        assert clnt.cert is False
        assert clnt.client is None
        assert clnt.log.level == logging.INFO

    def test_client_init_base_url_invalid_with_rest_path(self):
        with pytest.raises(ACTRESTAPIError):
            ACTClient(api_key="TEST", base_url="lab.act.arista.com/rest/v1")

    def test_client_init_base_url_invalid_no_tenant_identifier(self):
        with pytest.raises(ACTRESTAPIError):
            ACTClient(api_key="TEST", base_url="act.arista.com")

    def test_client_init_base_url_http(self):
        with pytest.raises(ACTRESTAPIError):
            ACTClient(api_key="TEST", base_url="http://lab.act.arista.com")

    def test_client_init_base_url_missing_forward_slash(self):
        with pytest.raises(ACTRESTAPIError):
            ACTClient(api_key="TEST", base_url="https:/lab.act.arista.com")

    def test_client_init_invalid_log_level(self):
        clnt = ACTClient(api_key="TEST", base_url=TEST_ACT_REST_API_BASE_URL, log_level="INVALID")
        assert clnt.api_key == "TEST"
        assert clnt.token is None
        assert clnt.base_url == TEST_ACT_REST_API_BASE_URL
        assert clnt.full_url == f"{TEST_ACT_REST_API_BASE_URL}{ACT_REST_API_PATH}"
        assert clnt.cert is False
        assert clnt.client is None
        assert clnt.log.level == logging.INFO

    def test_client_init_valid_log_level(self):
        clnt = ACTClient(api_key="TEST", base_url=TEST_ACT_REST_API_BASE_URL, log_level="DEBUG")
        assert clnt.api_key == "TEST"
        assert clnt.token is None
        assert clnt.base_url == TEST_ACT_REST_API_BASE_URL
        assert clnt.full_url == f"{TEST_ACT_REST_API_BASE_URL}{ACT_REST_API_PATH}"
        assert clnt.cert is False
        assert clnt.client is None
        assert clnt.log.level == logging.DEBUG

    def test_client_init_log_stdout(self):
        clnt = ACTClient(api_key="TEST", base_url=TEST_ACT_REST_API_BASE_URL, log_stdout=True)
        assert clnt.api_key == "TEST"
        assert clnt.token is None
        assert clnt.base_url == TEST_ACT_REST_API_BASE_URL
        assert clnt.full_url == f"{TEST_ACT_REST_API_BASE_URL}{ACT_REST_API_PATH}"
        assert clnt.cert is False
        assert clnt.client is None
        assert clnt.log.level == logging.INFO

    def test_client_init_log_file(self):
        clnt = ACTClient(
            api_key="TEST",
            base_url=TEST_ACT_REST_API_BASE_URL,
            log_file="run_unittests.log",
        )
        assert clnt.api_key == "TEST"
        assert clnt.token is None
        assert clnt.base_url == TEST_ACT_REST_API_BASE_URL
        assert clnt.full_url == f"{TEST_ACT_REST_API_BASE_URL}{ACT_REST_API_PATH}"
        assert clnt.cert is False
        assert clnt.client is None
        assert clnt.log.level == logging.INFO
        # Cleanup log file
        try:
            os.remove("run_unittests.log")
        except OSError:
            pass

    def test_client_validate_response(self):
        clnt = ACTClient(api_key="TEST", base_url=TEST_ACT_REST_API_BASE_URL)
        assert clnt.api_key == "TEST"
        resp = MockHttpxResponseValid()
        data = clnt._validate_response(resp)
        assert data == {"data": "data"}

    def test_client_validate_response_none(self):
        clnt = ACTClient(api_key="TEST", base_url=TEST_ACT_REST_API_BASE_URL)
        assert clnt.api_key == "TEST"
        data = clnt._validate_response(None)
        assert data == {}

    def test_client_validate_response_not_ok(self):
        clnt = ACTClient(api_key="TEST", base_url=TEST_ACT_REST_API_BASE_URL)
        assert clnt.api_key == "TEST"
        resp = MockHttpxResponseNotOK()
        data = clnt._validate_response(resp)
        assert data == {}

    def test_client_validate_response_invalid_json(self):
        clnt = ACTClient(api_key="TEST", base_url=TEST_ACT_REST_API_BASE_URL)
        assert clnt.api_key == "TEST"
        resp = MockHttpxResponseInvalidJSON()
        data = clnt._validate_response(resp)
        assert data == {}

    def test_client_validate_response_uncaught_exception(self):
        clnt = ACTClient(api_key="TEST", base_url=TEST_ACT_REST_API_BASE_URL)
        assert clnt.api_key == "TEST"
        resp = MockHttpxResponseRaiseUncaughtException()
        with pytest.raises(Exception):
            clnt._validate_response(resp)

    def test_client_get_access_token(self, monkeypatch):
        def mock_httpx_post(*args, **kwargs):
            return MockHttpxGoodTokenResponse()

        # Mock httpx.post for get_access_token
        monkeypatch.setattr(httpx, "post", mock_httpx_post)

        clnt = ACTClient(api_key="TEST", base_url=TEST_ACT_REST_API_BASE_URL)
        assert clnt.api_key == "TEST"
        token = clnt.get_access_token()
        assert token == "mocktoken"

    def test_client_get_access_token_no_token(self, monkeypatch):
        def mock_httpx_post(*args, **kwargs):
            return MockHttpxNoTokenResponse()

        # Mock httpx.post for get_access_token
        monkeypatch.setattr(httpx, "post", mock_httpx_post)

        clnt = ACTClient(api_key="TEST", base_url=TEST_ACT_REST_API_BASE_URL)
        assert clnt.api_key == "TEST"
        with pytest.raises(ACTRESTAPIError):
            clnt.get_access_token()
