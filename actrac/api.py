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

import time

import yaml

from actrac.constants import LAB_STATE_STR_TO_INT_MAP
from actrac.errors import ACTRESTAPIError


class ACTAPI:
    """ACTAPI Class of useful actions utilizing the client."""

    def __init__(self, clnt):
        """Initialize the class.

        :param clnt (obj): A ACTClient object
        """
        self.clnt = clnt

    def available_node_versions(self, timeout=30):
        """:return: dict of available versions per node type.

        :param timeout: Timeout for API call.
        :return: list of dicts of operations information.
        Example resp - {...}
        """
        return self.clnt.get("/topologies/nodes", timeout=timeout)

    def read_operations(self, offset=0, page_size=200, timeout=30):
        """Read status of all operations.

        :param timeout: Timeout for API call.
        :return: list of dicts of operations information.
        Example resp - {...}
        """
        # Initialize the done state
        done = False
        operations = []
        while not done:
            # Keep requesting operations until the returned list is empty
            params = {
                "offset": offset,
                "pageSize": page_size,
            }
            resp = self.clnt.get("/operations", params=params, timeout=timeout)
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

    def read_operation(self, op_id, timeout=30):
        """Read status of an operation by its ID.

        :param timeout: Timeout for API call.
        :return: dict of operation information.
        Example resp - {...}
        """
        if not op_id:
            raise ACTRESTAPIError("A 'op_id' must be provided")
        return self.clnt.get(f"/operations/{op_id}", timeout=timeout)

    def poll_operation_by_id(self, op_id, poll_iterations=5, poll_sleep=20, request_timeout=30):
        """Poll provided operation ID for provided iterations with provided sleep.

        :param op_id: An operation ID.
        :param poll_iterations: ...
        :param poll_sleep: ...
        :param request_timeout: Timeout for individual operation API calls.
        :return: dict of operation information or None.
        Example resp - {...}
        """
        if not op_id:
            raise ACTRESTAPIError("An 'op_id' must be provided")
        resp = None
        for index in range(poll_iterations):
            self.clnt.log.info("Operation check iteration %s", index + 1)
            resp = self.read_operation(op_id, timeout=request_timeout)
            if resp["is_completed"]:
                self.clnt.log.info("Operation completed with status - %s", resp["status"])
                break
            time.sleep(poll_sleep)
        return resp

    def poll_operation(self, operation, poll_iterations=5, poll_sleep=20, request_timeout=30):
        """Poll provided operation for provided iterations with provided sleep.

        :param operation: An operation object.
        :param poll_iterations: ...
        :param poll_sleep: ...
        :param request_timeout: Timeout for individual operation API calls.
        :return: dict of operation information or None.
        Example resp - {...}
        """
        if not operation:
            raise ACTRESTAPIError("An 'operation' must be provided")
        schema = operation.get("schema_type")
        if schema != "operation_resource":
            raise ACTRESTAPIError(
                f"Object {schema} is not an operation object. Can't poll as an operation."
            )
        op_id = operation.get("id")
        self.clnt.log.info("Poll operation %s - %s", op_id, operation.get("operation_type"))
        return self.poll_operation_by_id(op_id, poll_iterations, poll_sleep, request_timeout)

    def read_topology(self, topology_definition_id=None, timeout=30):
        """Read topology.

        :param topology_definition_id: ID of topology to read.
        :param timeout: Timeout for API call.
        :return: dict of topology information.
        Example resp - {...}
        """
        if not topology_definition_id:
            raise ACTRESTAPIError("A 'topology_definition_id' must be provided")
        return self.clnt.get(f"/topologies/{topology_definition_id}", timeout=timeout)

    def read_topologies(  # noqa: PLR0913
        self,
        offset=0,
        page_size=200,
        name=None,
        user=None,
        topology_file=None,
        diagram_file=None,
        device_count=None,
        timeout=30,
    ):
        """Read all topologies.

        :param timeout: Timeout for API call.
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
            resp = self.clnt.get("/topologies", params=params, timeout=timeout)
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

    def create_topology(  # noqa: PLR0913
        self,
        name,
        topo_def_file_path,
        description="",
        diagram_file_path=None,
        timeout=30,
    ):
        """Create a topology.

        :param name: name of topology to create.
        :param description: description of new topology
        :param topo_def_file_path: path to topology file.
        :param timeout: Timeout for API call.
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not name:
            raise ACTRESTAPIError("A 'name' for the topology must be provided")
        if not topo_def_file_path:
            raise ACTRESTAPIError(
                "A path to a topolofy definition 'topo_def_file_path' must be provided"
            )
        # Read the topology file and convert to json data
        with open(topo_def_file_path, "r") as topo_in:
            yaml_topo = yaml.safe_load(topo_in)
        data = {"name": name, "description": description, "file": yaml_topo}
        if diagram_file_path:
            data["diagram_path"] = diagram_file_path
        return self.clnt.post("/topologies", data=data, timeout=timeout)

    def update_topology(  # noqa: PLR0913
        self,
        topo_id,
        name=None,
        topo_def_file_path=None,
        description=None,
        diagram_file_path=None,
        timeout=30,
    ):
        """Update a topology.

        :param topo_id: topology ID of topology to update.
        :param name: new name to update for the provided topology ID.
        :param description: new description to update for provided topology ID
        :param topo_def_file_path: new topology file path to update for provided topology ID.
        :param diagram_file_path: new diagram file to update for provided topology ID.
        :param timeout: Timeout for API call.
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not topo_id:
            raise ACTRESTAPIError("A topology ID as 'topo_id' to update must be provided")
        data = {}
        if name is not None:
            data["name"] = name
        if topo_def_file_path is not None:
            with open(topo_def_file_path, "r") as topo_in:
                yaml_topo = yaml.safe_load(topo_in)
            data["file"] = yaml_topo
        if description is not None:
            data["description"] = description
        if diagram_file_path is not None:
            data["diagram_path"] = diagram_file_path
        if not data:
            self.clnt.log.warning(
                "No parameters provided to udpate for topology with ID %s", topo_id
            )
            return None
        data["id"] = topo_id
        params = {
            "id": topo_id,
        }
        return self.clnt.patch(f"/topologies/{topo_id}", params=params, data=data, timeout=timeout)

    def delete_topology(self, topology_definition_id=None, timeout=30):
        """Delete a topology.

        :param topology_definition_id: ID of topology definition to delete.
        :param timeout: Timeout for API call.
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not topology_definition_id:
            raise ACTRESTAPIError("A 'topology_definition_id' must be provided")
        return self.clnt.delete(f"/topologies/{topology_definition_id}", timeout=timeout)

    def read_lab(self, lab_id, timeout=30):
        """Read a lab by ID.

        :param lab_id: ID of lab to get information for.
        :param timeout: Timeout for API call.
        :return: dict of lab information.
        Example resp - {...}
        """
        if not lab_id:
            raise ACTRESTAPIError("A valid 'lab_id' must be provided")
        return self.clnt.get(f"/labs/{lab_id}", timeout=timeout)

    def read_labs(  # noqa: PLR0913
        self,
        offset=0,
        page_size=200,
        name=None,
        user=None,
        topology_definition=None,
        state=None,
        timeout=30,
    ):
        """Read all labs.

        :param timeout: Timeout for API call.
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
                        self.clnt.log.error("read_labs: Invalid state string - %s", state)
                        return None
                    params["state"] = LAB_STATE_STR_TO_INT_MAP[state]
                elif isinstance(state, int):
                    params["state"] = state
                else:
                    self.clnt.log.error("read_labs: Invalid state type - %s:%s", state, type(state))
                    return None
            resp = self.clnt.get("/labs", params=params, timeout=timeout)
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

    def create_lab(self, name=None, description="", topo_def=None, timeout=30):
        """Create a lab.

        :param name: name of lab to create.
        :param description: description of new lab
        :param topo_def: topology file path name. 'file_pathname' param from topology data.
        :param timeout: Timeout for API call.
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not name:
            raise ACTRESTAPIError("A 'name' for the lab must be provided")
        if not topo_def:
            raise ACTRESTAPIError("A topolofy definition 'topo_def' for the lab must be provided")
        data = {"name": name, "description": description, "topology_definition": topo_def}
        return self.clnt.post("/labs", data=data, timeout=timeout)

    def delete_lab(self, lab_id, timeout=30):
        """Delete a lab by ID.

        :param lab_id: ID of lab to delete.
        :param timeout: Timeout for API call.
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not lab_id:
            raise ACTRESTAPIError("A valid 'lab_id' must be provided")
        return self.clnt.delete(f"/labs/{lab_id}", timeout=timeout)

    def deploy_lab(self, lab_id, timeout=30):
        """Deploy an existing lab by ID.

        :param lab_id: ID of lab to deploy.
        :param timeout: Timeout for API call.
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not lab_id:
            raise ACTRESTAPIError("A valid 'lab_id' must be provided")
        return self.clnt.post(f"/labs/{lab_id}/deploy", timeout=timeout)

    def undeploy_lab(self, lab_id, timeout=30):
        """Undeploy an existing lab by ID.

        :param lab_id: ID of lab to undeploy.
        :param timeout: Timeout for API call.
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not lab_id:
            raise ACTRESTAPIError("A valid 'lab_id' must be provided")
        return self.clnt.post(f"/labs/{lab_id}/undeploy", timeout=timeout)

    def start_lab(self, lab_id, timeout=30):
        """Start an existing lab by ID.

        :param lab_id: ID of lab to start.
        :param timeout: Timeout for API call.
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not lab_id:
            raise ACTRESTAPIError("A valid 'lab_id' must be provided")
        return self.clnt.post(f"/labs/{lab_id}/start", timeout=timeout)

    def stop_lab(self, lab_id, timeout=30):
        """Stop an existing lab by ID.

        :param lab_id: ID of lab to stop.
        :param timeout: Timeout for API call.
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not lab_id:
            raise ACTRESTAPIError("A valid 'lab_id' must be provided")
        return self.clnt.post(f"/labs/{lab_id}/stop", timeout=timeout)

    def read_user(self, user_id, timeout=30):
        """Read a user by ID.

        :param user_id: ID of user to get information for.
        :param timeout: Timeout for API call.
        :return: dict of user information.
        Example resp - {...}
        """
        if not user_id:
            raise ACTRESTAPIError("A valid 'user_id' must be provided")
        if not isinstance(user_id, int):
            raise ACTRESTAPIError("Invalid 'user_id' type. Must be an integer")
        return self.clnt.get(f"/users/{user_id}", timeout=timeout)

    def read_users(  # noqa: PLR0913, PLR0912
        self,
        offset=0,
        page_size=200,
        user_name=None,
        first_name=None,
        last_name=None,
        email_addr=None,
        group_id=None,
        status=None,
        timeout=30,
    ):
        """Read all users.

        :param timeout: Timeout for API call.
        :return: list of dicts of all users information.
        Example resp - {...}
        """
        # Initialize done state
        done = False
        # Initialize the users list
        users = []
        while not done:
            # Keep requesting users until the returned list is empty
            params = {
                "offset": offset,
                "pageSize": page_size,
            }
            if user_name:
                params["user_name"] = user_name
            if first_name:
                params["first_name"] = first_name
            if last_name:
                params["last_name"] = last_name
            if email_addr:
                params["email_addr"] = email_addr
            if group_id:
                if not isinstance(group_id, int):
                    raise ACTRESTAPIError("Invalid 'group_id' type. Must be an integer")
                params["group_id"] = group_id
            if status is not None:
                if isinstance(status, str):
                    if status not in LAB_STATE_STR_TO_INT_MAP:
                        self.clnt.log.error("read_users: Invalid status string - %s", status)
                        return None
                    params["status"] = LAB_STATE_STR_TO_INT_MAP[status]
                elif isinstance(status, int):
                    params["status"] = status
                else:
                    self.clnt.log.error(
                        "read_users: Invalid status type - %s:%s", status, type(status)
                    )
                    return None
            resp = self.clnt.get("/users", params=params, timeout=timeout)
            # Get the new users from this resp
            new_users = resp.get("result", [])
            if not new_users:
                # If no new users returned, we are done
                done = True
                continue
            users.extend(new_users)
            page_size = resp.get("pageSize", page_size)
            total = resp.get("total")
            if total and total <= page_size:
                done = True
                continue
            # Adjust the offset to the next page
            offset += page_size
        return users

    def read_groups(self, offset=0, page_size=200, timeout=30):
        """Read all groups.

        :param timeout: Timeout for API call.
        :return: list of dicts of all groups information.
        Example resp - {...}
        """
        # Initialize done state
        done = False
        # Initialize the groups list
        groups = []
        while not done:
            # Keep requesting groups until the returned list is empty
            params = {
                "offset": offset,
                "pageSize": page_size,
            }
            resp = self.clnt.get("/groups", params=params, timeout=timeout)
            # Get the new groups from this resp
            new_groups = resp.get("result", [])
            if not new_groups:
                # If no new groups returned, we are done
                done = True
                continue
            groups.extend(new_groups)
            page_size = resp.get("pageSize", page_size)
            total = resp.get("total")
            if total and total <= page_size:
                done = True
                continue
            # Adjust the offset to the next page
            offset += page_size
        return groups
