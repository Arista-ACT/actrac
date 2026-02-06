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

"""example_lab_action ..."""

import argparse
import logging

from actrac.client import ACTClient


def parseargs():
    """Parseargs ..."""
    parser = argparse.ArgumentParser(description="ACT REST API Test")
    parser.add_argument(
        "--api_key", dest="api_key", required=True, action="store", help="ACT REST API KEY"
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
        "--topology_definition",
        dest="topology_definition",
        required=False,
        action="store",
        help="Existing topology definition file. Both file and name are required to create",
    )
    parser.add_argument(
        "--lab_name",
        dest="lab_name",
        required=False,
        action="store",
        help="Name for creating a lab. Both file and name are required to create",
    )
    parser.add_argument("--logging", action="store_true", default=False, help="Enable logging")
    args = parser.parse_args()
    return args


def run_lab_actions(api_key, base_url=None, topology_definition=None, lab_name=None):
    """run_lab_actions ..."""
    client = ACTClient(api_key=api_key, base_rul=base_url, log_stdout=True)
    print("INSTANTIATE CLIENT")
    print("")
    client.connect()
    print("CONNECTED")
    print("")

    print("READ LABS")
    print("")
    labs = client.api.read_labs()
    print(f"Found {len(labs)} labs")
    print("")

    if topology_definition is not None and lab_name is not None:
        print("CREATE ACTRAC TEST TOPO")
        resp = client.api.create_lab(
            name=lab_name,
            description=f"{lab_name} description",
            topo_def=topology_definition,
        )
        print(resp)
        client.api.poll_operation(resp)
    print("")

    print("")
    print("DISCONNECT CLIENT")
    print("")
    client.disconnect()
    print("LOGGED OUT")
    print("")


def main():
    """Begin example of ACT REST API Client Lab Functions."""
    options = parseargs()
    if options.logging:
        logging.basicConfig(
            filename="labactionstest.log", format="%(levelname)s: %(message)s", level=logging.DEBUG
        )
    print("ACT REST API CLIENT LAB ACTIONS TEST")
    print("")
    run_lab_actions(
        options.api_key, options.base_url, options.topology_definition, options.lab_name
    )
    print("DONE")
    print("")


if __name__ == "__main__":
    main()
