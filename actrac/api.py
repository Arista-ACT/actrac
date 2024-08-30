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

"""API wrapper functions for interacting with the ACT REST API."""

from actrac.constants import LAB_STATE_STR_TO_INT_MAP
from actrac.errors import ACTRESTAPIError


class ACTAPI:
    """ACTAPI Class of useful actions utilizing the client."""

    def __init__(self, clnt):
        """Initialize the class.

        :param clnt (obj): A ACTClient object
        """
        self.clnt = clnt

    def available_node_versions(self):
        """:return: dict of available versions per node type.

        Example resp - {...}
        """
        return self.clnt.get("/topologies/nodes")

    def read_operations(self, offset=0, page_size=200):
        """Read status of all operations."""
        # Initialize the done state
        done = False
        operations = []
        while not done:
            # Keep requesting operations until the returned list is empty
            params = {
                "offset": offset,
                "pageSize": page_size,
            }
            resp = self.clnt.get("/operations", params=params)
            # Get the new operations from this resp
            new_ops = resp.get("result", [])
            if not new_ops:
                # If no new operations returned, we are done
                done = True
                continue
            # Add the newly found user topo to the master user topo list
            operations.extend(new_ops)
            page_size = resp.get("pageSize", page_size)
            total = resp.get("total")
            if total and total <= page_size:
                done = True
                continue
            # Adjust the offset to the next page
            offset += page_size
        return operations

    def read_operation(self, op_id):
        """Read status of an operation by its ID."""
        if not op_id:
            raise ACTRESTAPIError("A 'op_id' must be provided")
        return self.clnt.get(f"/operations/{op_id}")

    def validate_topology_file(self, file, timeout=60):
        """Validate provide topology file.

        :param file: file name already uploaded to ACT.
        :param timeout: Timeout for validation of topology file to complete.
        :return: dict of validation resp message.

        Example:
        -------
        {'originator_message_id': '362582560 - 3',
         'op': 'validate_topology',
         'data': {'file': 'topologies/TestTopologyFile.yml'},
         'topic': 'topology_definition_status',
         'status': 'success'}
        """
        pass

    def read_topology(self, topology_definition_id=None):
        """Read topology.

        :param topology_definition_id: ID of topology to read.
        :return: dict of topology information.
        Example resp - {...}
        """
        if not topology_definition_id:
            raise ACTRESTAPIError("A 'topology_definition_id' must be provided")
        return self.clnt.get(f"/topologies/{topology_definition_id}")

    def read_topologies(  # noqa: PLR0913
        self,
        offset=0,
        page_size=200,
        name=None,
        user=None,
        topology_file=None,
        diagram_file=None,
        device_count=None,
    ):
        """Read all topologies.

        :return: dict of all topologies information.
        Example resp - {...}
        """
        # Initialize done state
        done = False
        topos = []
        while not done:
            # Keep requesting topologies until the returned list is empty
            params = {
                "offset": offset,
                "pageSize": page_size,
            }
            if name:
                params["name"] = name
            if user:
                params["created_by"] = user
            if topology_file:
                params["topology_pathname"] = topology_file
            if diagram_file:
                params["diagram_pathname"] = diagram_file
            if device_count is not None:
                params["device_count"] = device_count
            resp = self.clnt.get("/topologies", params=params)
            # Get the new topos from this resp
            new_topos = resp.get("result", [])
            if not new_topos:
                # If no new topos returned, we are done
                done = True
                continue
            # Add the newly found user topo to the master user topo list
            topos.extend(new_topos)
            page_size = resp.get("pageSize", page_size)
            total = resp.get("total")
            if total and total <= page_size:
                done = True
                continue
            # Adjust the offset to the next page
            offset += page_size
        return topos

    def delete_topology(self, topology_definition_id=None):
        """Delete a topology.

        :param topology_definition_id: ID of topology definition to delete.
        :param name: name of topology definition to delete.
        :param file: file of topology definition to delete.
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not topology_definition_id:
            raise ACTRESTAPIError("A 'topology_definition_id' must be provided")
        return self.clnt.delete(f"/topologies/{topology_definition_id}")

    def read_lab(self, lab_id):
        """Read a lab by ID.

        :param lab_id: ID of lab to get information for.
        :return: dict of lab information.
        Example resp - {...}
        """
        if not lab_id:
            raise ACTRESTAPIError("A valid 'lab_id' must be provided")
        return self.clnt.get(f"/labs/{lab_id}")

    def read_labs(  # noqa: PLR0913
        self,
        offset=0,
        page_size=200,
        name=None,
        user=None,
        topology_definition=None,
        state=None,
    ):
        """Read all labs.

        :return: dict of all labs information.
        Example resp - {...}
        """
        # Initialize done state
        done = False
        # Initialize the labs list
        labs = []
        while not done:
            # Keep requesting labs until the returned list is empty
            params = {
                "offset": offset,
                "pageSize": page_size,
            }
            if name:
                params["name"] = name
            if user:
                params["user"] = user
            if topology_definition:
                params["topology_definition"] = topology_definition
            if state is not None:
                if isinstance(state, str):
                    if state not in LAB_STATE_STR_TO_INT_MAP:
                        print("INVALID STATE STRING")
                        return None
                    params["state"] = LAB_STATE_STR_TO_INT_MAP[state]
                elif isinstance(state, int):
                    params["state"] = state
                else:
                    print("INVALID STATE TYPE")
                    return None
            resp = self.clnt.get("/labs", params=params)
            # Get the new labs from this resp
            new_labs = resp.get("result", [])
            if not new_labs:
                # If no new labs returned, we are done
                done = True
                continue
            labs.extend(new_labs)
            page_size = resp.get("pageSize", page_size)
            total = resp.get("total")
            if total and total <= page_size:
                done = True
                continue
            # Adjust the offset to the next page
            offset += page_size
        return labs

    def create_lab(self, name=None, description="", topo_def=None):
        """Create a lab.

        :param name: ID of lab to delete.
        :param description: ...
        :param topo_def: ...
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not name:
            raise ACTRESTAPIError("A 'name' for the lab must be provided")
        if not topo_def:
            raise ACTRESTAPIError("A topolofy definition 'topo_def' for the lab must be provided")
        data = {"name": name, "description": description, "topology_definition": topo_def}
        return self.clnt.post("/labs", data=data)

    def delete_lab(self, lab_id):
        """Delete a lab by ID.

        :param lab_id: ID of lab to delete.
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not lab_id:
            raise ACTRESTAPIError("A valid 'lab_id' must be provided")
        return self.clnt.delete(f"/labs/{lab_id}")

    def deploy_lab(self, lab_id):
        """Deploy an existing lab by ID.

        :param lab_id: ID of lab to deploy.
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not lab_id:
            raise ACTRESTAPIError("A valid 'lab_id' must be provided")
        return self.clnt.post(f"/labs/{lab_id}/deploy")

    def undeploy_lab(self, lab_id):
        """Undeploy an existing lab by ID.

        :param lab_id: ID of lab to undeploy.
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not lab_id:
            raise ACTRESTAPIError("A valid 'lab_id' must be provided")
        return self.clnt.post(f"/labs/{lab_id}/undeploy")

    def start_lab(self, lab_id):
        """Start an existing lab by ID.

        :param lab_id: ID of lab to start.
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not lab_id:
            raise ACTRESTAPIError("A valid 'lab_id' must be provided")
        return self.clnt.post(f"/labs/{lab_id}/start")

    def stop_lab(self, lab_id):
        """Stop an existing lab by ID.

        :param lab_id: ID of lab to stop.
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not lab_id:
            raise ACTRESTAPIError("A valid 'lab_id' must be provided")
        return self.clnt.post(f"/labs/{lab_id}/stop")
