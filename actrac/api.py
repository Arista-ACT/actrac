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

from datetime import datetime
from actrac.constants import LAB_STATE_STR_TO_INT_MAP
from actrac.errors import ACTRESTAPIError


class ACTAPI:
    """ACTAPI Class of useful actions utilizing the client."""

    def __init__(self, clnt):
        """Initialize the class.

        :param clnt (obj): A ACTClient object
        """
        self.clnt = clnt

    def _read_all_via_paging(  # noqa: PLR0913
        self,
        api_endpoint,
        params=None,
        offset=0,
        page_size=200,
        timeout=30,
    ):
        """Read all objects for provided URL via polling pageSize using provided params.

        :param timeout: Timeout for API call.
        :return: list of dicts of all objects information.
        Example resp - {...}
        """
        # Initialize params if None provided
        if not params:
            params = {}
        # Add pageSize to params
        params["pageSize"] = page_size
        # Initialize the objects list
        objects = []
        # Initialize done state
        done = False
        while not done:
            # Add offset to params and update it every loop iteration.
            params["offset"] = offset
            # Keep requesting objects until the returned list is empty
            resp = self.clnt.get(api_endpoint, params=params, timeout=timeout)
            # Get the new objects from this resp
            new_objs = resp.get("result", [])
            if not new_objs:
                # If no new objects returned, we are done
                done = True
                continue
            objects.extend(new_objs)
            page_size = resp.get("pageSize", page_size)
            total = resp.get("total")
            if total and total <= page_size:
                done = True
                continue
            # Adjust the offset to the next page
            offset += page_size
        return objects

    def read_operations(self, offset=0, page_size=200, timeout=30):
        """Read status of all operations.

        :param timeout: Timeout for API call.
        :return: list of dicts of operations information.
        Example resp - {...}
        """
        return self._read_all_via_paging("/operations", None, offset, page_size, timeout)

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
            self.clnt.log.info(resp)
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

    def available_node_versions(self, timeout=30):
        """:return: dict of available versions per node type.

        :param timeout: Timeout for API call.
        :return: list of dicts of operations information.
        Example resp - {...}
        """
        return self.clnt.get("/topologies/nodes", timeout=timeout)

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
        # Initialize params for read topologies query
        params = {}
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
        return self._read_all_via_paging("/topologies", params, offset, page_size, timeout)

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
                "No parameters provided to update for topology with ID %s", topo_id
            )
            return None
        return self.clnt.patch(f"/topologies/{topo_id}", data=data, timeout=timeout)

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
        # Initialize params for read topologies query
        params = {}
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
        return self._read_all_via_paging("/labs", params, offset, page_size, timeout)

    def create_lab(self, name=None, description="", topo_def=None, timeout=30):
        """Create a lab.

        :param name: name of lab to create.
        :param description: description of new lab
        :param topo_def: topology file name. 'file_pathname' param from topology data.
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

    def update_lab(  # noqa: PLR0913
        self,
        lab_id,
        name=None,
        description=None,
        timeout=30,
    ):
        """Update a lab.

        :param lab_id: Lab ID of lab to update.
        :param name: new name to update for the provided topology ID.
        :param description: new description to update for provided topology ID
        :param timeout: Timeout for API call.
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not lab_id:
            raise ACTRESTAPIError("A lab ID as 'lab_id' to update must be provided")
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if not data:
            self.clnt.log.warning("No parameters provided to update for lab with ID %s", lab_id)
            return None
        return self.clnt.patch(f"/labs/{lab_id}", data=data, timeout=timeout)

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
        # Initialize params for read topologies query
        params = {}
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
                self.clnt.log.error("read_users: Invalid status type - %s:%s", status, type(status))
                return None
        return self._read_all_via_paging("/users", params, offset, page_size, timeout)

    def create_user(  # noqa: PLR0913
        self,
        user_name,
        password,
        group_id,
        first_name=None,
        last_name=None,
        email_address=None,
        timeout=30,
    ):
        """Create a user.

        :param user_name: user name for new user being created.
        :param password: password for new user being created.
        :param group_id: ...
        :param first_name: ...
        :param last_name: ...
        :param email_address: ...
        :param timeout: Timeout for API call.
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not user_name:
            raise ACTRESTAPIError("A 'user_name' for the user must be provided")
        if not password:
            raise ACTRESTAPIError("A 'password' for the user must be provided")
        if group_id is None:
            raise ACTRESTAPIError("A 'group_id' for the user must be provided")
        elif not isinstance(group_id, int):
            raise ACTRESTAPIError("Invalid 'group_id' type. Must be an integer")
        elif group_id == 0:
            raise ACTRESTAPIError("'group_id' can not be 0.")

        data = {"user_name": user_name, "password": password, "group_id": group_id}
        if first_name is not None:
            data["first_name"] = first_name
        if last_name is not None:
            data["last_name"] = last_name
        if email_address is not None:
            data["email_address"] = email_address
        return self.clnt.post("/users", data=data, timeout=timeout)

    def update_user(  # noqa: PLR0913
        self,
        user_id,
        first_name=None,
        last_name=None,
        email_address=None,
        group_id=None,
        timeout=30,
    ):
        """Update a user.

        :param user_id: User ID of user to update.
        :param first_name: new first name to update for the provided user ID.
        :param last_name: new last name to update for the provided user ID.
        :param email_address: new email address to update for provided user ID.
        :param group_id: new group ID to update for provided user ID.
        :param timeout: Timeout for API call.
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not user_id:
            raise ACTRESTAPIError("A user ID as 'user_id' to update must be provided")
        data = {}
        if first_name is not None:
            data["first_name"] = first_name
        if last_name is not None:
            data["last_name"] = last_name
        if email_address is not None:
            data["email_address"] = email_address
        if group_id is not None:
            if not isinstance(group_id, int):
                raise ACTRESTAPIError("Invalid 'group_id' type. Must be an integer")
            if group_id == 0:
                raise ACTRESTAPIError("'group_id' can not be 0.")
            data["group_id"] = group_id
        if not data:
            self.clnt.log.warning("No parameters provided to update for user with ID %s", user_id)
            return None
        return self.clnt.patch(f"/users/{user_id}", data=data, timeout=timeout)

    def delete_user(self, user_id, timeout=30):
        """Delete a user by ID.

        :param user_id: ID of user to delete.
        :param timeout: Timeout for API call.
        :return: dict of resp/results.
        Example resp - {...}
        """
        if not user_id:
            raise ACTRESTAPIError("A valid 'user_id' must be provided")
        return self.clnt.delete(f"/users/{user_id}", timeout=timeout)

    def read_groups(self, offset=0, page_size=200, timeout=30):
        """Read all groups.

        :param timeout: Timeout for API call.
        :return: list of dicts of all groups information.
        Example resp - {...}
        """
        return self._read_all_via_paging("/groups", None, offset, page_size, timeout)

    def create_api_key_for(self, user_id, description, expiration_date, timeout=30):
        """Creates an API key for a user.

        ** Need Admin Role to use this functionality **

        :param user_id (int): Users Id.
        :param description (str): API Key Description.
        :param expiration_date (datetime): API Key Expiration Date.
        :param timeout: Timeout for API call.
        :return: dict Operation Record.
        Example resp - {...}
        """
        if not user_id:
            raise ACTRESTAPIError("A user ID as 'user_id' to create an API key must be provided")
        else:
            if not isinstance(user_id, int):
                raise ACTRESTAPIError("Invalid 'user_id' type. Must be an integer")

        if not description:
            raise ACTRESTAPIError("A description as 'description' to create an API key must be provided")
        else:
            if not isinstance(description, str):
                raise ACTRESTAPIError("Invalid 'description' type. Must be an string")

        if not expiration_date:
            raise ACTRESTAPIError("An expiration date as 'expiration_date' to create an API key must be provided")
        else:
            if not isinstance(expiration_date, datetime):
                raise ACTRESTAPIError("Invalid 'expiration_date' type. Must be a datetime")

        data = {
            "user_id": user_id,
            "description": description,t
            "expiration_date": expiration_date.strftime("%d-%m-%Y")
        }

        return self.clnt.post("/auth/apikey", data=data, timeout)

    def delete_api_key_for(self, id, timeout=30):
        """Deletes an API key for a user.

        ** Need Admin Role to use this functionality **

        :param id: API key 'id' field.
        :param timeout: Timeout for API call.
        :return: dict with 'id' field of deleted api key.
        Example resp - {...}
        """
        if not id:
            raise ACTRESTAPIError("An API key 'id' as 'id' to delete an API key must be provided")
        else:
            if not isinstance(id, int):
                raise ACTRESTAPIError("Invalid 'id' type. Must be an integer")

        return self.clnt.delete(f"/auth/apikey/{id}", None, offset, page_size, timeout)


    def list_api_keys_for(self, user_id, timeout=30):
        """Lists API keys for a user.

        ** Need Admin Role to use this functionality **

        :param timeout: Timeout for API call.
        :return: list of dicts of all groups information.
        Example resp - {...}
        """

        if not user_id:
            raise ACTRESTAPIError("A user ID as 'user_id' to list a user's API keys must be provided")
        else:
            if not isinstance(user_id, int):
                raise ACTRESTAPIError("Invalid 'user_id' type. Must be an integer")

        return self.clnt.get(f"/auth/apikey?&user_id={user_id}", timeout)