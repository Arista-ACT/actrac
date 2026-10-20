#
# Copyright (c) 2026, Arista Networks, Inc.
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

import json

import httpx
import pytest

from actrac.client import ACTClient

TEST_ACT_REST_API_BASE_URL = "https://lab.act.arista.com"
UPLOADED_DIAGRAM_ID = "diagram-0f3c.png"


@pytest.fixture
def recorded_client():
    """Return a connected client whose requests are captured instead of sent."""
    requests = []

    def handler(request):
        requests.append(request)
        if request.method == "POST" and request.url.path.endswith("/topologies/diagram"):
            return httpx.Response(200, json={"diagram_id": UPLOADED_DIAGRAM_ID})
        return httpx.Response(200, json={"id": "operation-id"})

    clnt = ACTClient(api_key="TEST", base_url=TEST_ACT_REST_API_BASE_URL)
    clnt.client = httpx.Client(base_url=clnt.full_url, transport=httpx.MockTransport(handler))
    return clnt, requests


@pytest.fixture
def diagram_png(tmp_path):
    path = tmp_path / "diagram.png"
    path.write_bytes(b"\x89PNG\r\n\x1a\nnot-a-real-image")
    return path


@pytest.fixture
def topology_yaml(tmp_path):
    path = tmp_path / "topology.yml"
    path.write_text("nodes: []\n")
    return path


def assert_diagram_upload(request):
    assert request.method == "POST"
    assert request.url.path.endswith("/topologies/diagram")
    assert request.headers["content-type"].startswith("multipart/form-data")
    body = request.read()
    assert b'name="diagram"; filename="diagram.png"' in body
    assert b"Content-Type: image/png" in body


class TestUpdateTopologyDiagramRemoval:
    """The ACT API removes the current diagram when an update sends an empty diagram_id."""

    def test_empty_diagram_path_requests_removal_without_upload(self, recorded_client):
        clnt, requests = recorded_client

        clnt.api.update_topology("topo-1", diagram_file_path="")

        assert [(r.method, r.url.path) for r in requests] == [
            ("PATCH", "/rest/v1/topologies/topo-1")
        ]
        assert json.loads(requests[0].read()) == {"diagram_id": ""}


class TestDiagramUpload:
    """Diagram uploads during topology create and update."""

    def test_update_topology_uploads_png_then_patches_diagram_id(
        self, recorded_client, diagram_png
    ):
        clnt, requests = recorded_client

        clnt.api.update_topology("topo-1", diagram_file_path=str(diagram_png))

        upload, update = requests
        assert_diagram_upload(upload)
        assert (update.method, update.url.path) == ("PATCH", "/rest/v1/topologies/topo-1")
        assert json.loads(update.read()) == {"diagram_id": UPLOADED_DIAGRAM_ID}

    def test_create_topology_uploads_png_then_posts_diagram_id(
        self, recorded_client, diagram_png, topology_yaml
    ):
        clnt, requests = recorded_client

        clnt.api.create_topology(
            "TOPO",
            topo_def_file_path=str(topology_yaml),
            diagram_file_path=str(diagram_png),
        )

        upload, create = requests
        assert_diagram_upload(upload)
        assert (create.method, create.url.path) == ("POST", "/rest/v1/topologies")
        assert json.loads(create.read()) == {
            "name": "TOPO",
            "description": "",
            "file": {"nodes": []},
            "diagram_id": UPLOADED_DIAGRAM_ID,
        }

    def test_update_topology_without_diagram_leaves_diagram_unchanged(self, recorded_client):
        clnt, requests = recorded_client

        clnt.api.update_topology("topo-1", name="renamed")

        assert [(r.method, r.url.path) for r in requests] == [
            ("PATCH", "/rest/v1/topologies/topo-1")
        ]
        assert json.loads(requests[0].read()) == {"name": "renamed"}
