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

from actrac.client import ACTClient
from actrac.constants import ACT_REST_API_BASE_URL, ACT_REST_API_PATH


class TestACTClient:
    """TestACTClient."""

    def test_client_init(self):
        clnt = ACTClient(api_key="TEST")
        assert clnt.api_key == "TEST"
        assert clnt.token is None
        assert clnt.base_url == ACT_REST_API_BASE_URL
        assert clnt.full_url == f"{ACT_REST_API_BASE_URL}{ACT_REST_API_PATH}"
        assert clnt.cert is False
        assert clnt.client is None
        assert clnt.log.level == logging.INFO

    def test_client_init_invalid_log_level(self):
        clnt = ACTClient(api_key="TEST", log_level="INVALID")
        assert clnt.api_key == "TEST"
        assert clnt.token is None
        assert clnt.base_url == ACT_REST_API_BASE_URL
        assert clnt.full_url == f"{ACT_REST_API_BASE_URL}{ACT_REST_API_PATH}"
        assert clnt.cert is False
        assert clnt.client is None
        assert clnt.log.level == logging.INFO

    def test_client_init_valid_log_level(self):
        clnt = ACTClient(api_key="TEST", log_level="DEBUG")
        assert clnt.api_key == "TEST"
        assert clnt.token is None
        assert clnt.base_url == ACT_REST_API_BASE_URL
        assert clnt.full_url == f"{ACT_REST_API_BASE_URL}{ACT_REST_API_PATH}"
        assert clnt.cert is False
        assert clnt.client is None
        assert clnt.log.level == logging.DEBUG

    def test_client_init_log_stdout(self):
        clnt = ACTClient(api_key="TEST", log_stdout=True)
        assert clnt.api_key == "TEST"
        assert clnt.token is None
        assert clnt.base_url == ACT_REST_API_BASE_URL
        assert clnt.full_url == f"{ACT_REST_API_BASE_URL}{ACT_REST_API_PATH}"
        assert clnt.cert is False
        assert clnt.client is None
        assert clnt.log.level == logging.INFO

    def test_client_init_log_file(self):
        clnt = ACTClient(api_key="TEST", log_file="run_unittests.log")
        assert clnt.api_key == "TEST"
        assert clnt.token is None
        assert clnt.base_url == ACT_REST_API_BASE_URL
        assert clnt.full_url == f"{ACT_REST_API_BASE_URL}{ACT_REST_API_PATH}"
        assert clnt.cert is False
        assert clnt.client is None
        assert clnt.log.level == logging.INFO
        # Cleanup log file
        try:
            os.remove("run_unittests.log")
        except OSError:
            pass
