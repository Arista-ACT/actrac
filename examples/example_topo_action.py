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

"""example_topo_action ..."""

import argparse
import logging
import os

from actrac.client import ACTClient


def parseargs():
    """Parseargs ..."""
    parser = argparse.ArgumentParser(description="ACT REST API Test")
    parser.add_argument(
        "--api_key", dest="api_key", required=True, action="store", help="ACT REST API Key"
    )
    parser.add_argument(
        "--base_url",
        dest="base_url",
        required=True,
        action="store",
        default="https://lab.act.arista.com",
        help="Tenant base URL",
    )
    parser.add_argument(
        "--topology_file",
        dest="topology_file",
        required=False,
        action="store",
        help="Path to file for creating a topology. Both file and name are required to create",
    )
    parser.add_argument(
        "--topology_name",
        dest="topology_name",
        required=False,
        action="store",
        help="Name for creating a topology. Both file and name are required to create",
    )
    parser.add_argument("--logging", action="store_true", default=False, help="Enable logging")
    args = parser.parse_args()
    return args


def run_topo_actions(api_key, base_url=None, topology_file=None, topology_name=None):
    """run_topo_actions ..."""
    client = ACTClient(api_key=api_key, base_url=base_url, log_stdout=True)
    print("INSTANTIATE CLIENT")
    print("")
    client.connect()
    print("CONNECTED")
    print("")

    print("")
    print("READ TOPOLOGIES VIA TOPOLOGIES QUERY")
    print("")
    resp = client.api.read_topologies()
    print(len(resp))
    print("")
    for topo in resp:
        print(f"{topo['name']} - {topo['topology_pathname']}")
    print("")

    if topology_file is not None and topology_name is not None:
        print("")
        if os.path.isfile(topology_file):
            print(f"TEST CREATE TOPOLOGY WITH FILE - {topology_file}")
            resp = client.api.create_topology(
                name=topology_name,
                topo_def_file_path=topology_file,
                description=f"{topology_name} description",
                diagram_file_path=None,
            )
            print(resp)
            print("")
            client.api.poll_operation(resp)
        else:
            print("NO FILE WITH PROVIDED NAME FOUND")
    else:
        print("NOT CREATING TOPOLOGY. EITHER FILE OR NAME NOT PROVIDED.")

    print("")
    print("DISCONNECT CLIENT")
    print("")
    client.disconnect()
    print("LOGGED OUT")
    print("")


def main():
    """Begin example of ACT REST API Client Topology Functions."""
    options = parseargs()
    if options.logging:
        logging.basicConfig(
            filename="topoactionstest.log", format="%(levelname)s: %(message)s", level=logging.DEBUG
        )
    print("ACT REST API CLIENT TOPOLOGY ACTIONS TEST")
    print("")
    run_topo_actions(
        options.api_key, options.base_url, options.topology_file, options.topology_name
    )
    print("DONE")
    print("")


if __name__ == "__main__":
    main()
