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

    def validate_topology_file(self, name, file, timeout=30):
        """Validate provide topology file.

        :param name: name for topology to be validated.
        :param file: file name with topology contents to be validated.
        :param timeout: Timeout for API call.
        :return: dict of validation resp message.
        """
        file_contents = f"{file}"
        data = {
            "name": name,
            "file": file_contents,
        }
        return self.clnt.post("/topologies/validate", data=data, timeout=timeout)

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
