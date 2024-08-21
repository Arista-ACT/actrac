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

        Example response - {...}
        """
        response = self.clnt.get("/topologies/nodes")
        return response.json()

    def read_operations(self):
        """Read status of all operations."""
        # Initialize the offset
        offset = 0
        # Initialize the done state
        done = False
        operations = []
        while not done:
            # Keep requesting operations until the returned list is empty
            params = {"offset": offset}
            response = self.clnt.get("/operations", params=params)
            # Get the new operations from this response
            new_ops = response.json().get("result", [])
            if not new_ops:
                # If no new operations returned, we are done
                done = True
                continue
            # Add the newly found user topo to the master user topo list
            operations.extend(new_ops)
            # Adjust the offset to the next page
            offset += response.json().get("pageSize")
        return operations

    def read_operation(self, op_id):
        """Read status of an operation by its ID."""
        if not op_id:
            raise ACTRESTAPIError("A 'op_id' must be provided")
        response = self.clnt.get(f"/operations/{op_id}")
        return response.json()

    def validate_topology_file(self, file, timeout=60):
        """Validate provide topology file.

        :param file: file name already uploaded to ACT.
        :param timeout: Timeout for validation of topology file to complete.
        :return: dict of validation response message.

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
        Example response - {...}
        """
        if not topology_definition_id:
            raise ACTRESTAPIError("A 'topology_definition_id' must be provided")
        response = self.clnt.get(f"/topologies/{topology_definition_id}")
        return response.json()

    def read_topologies(self):
        """Read all topologies.

        :return: dict of all topologies information.
        Example response - {...}
        """
        # Initialize the offset
        offset = 0
        # Initialize done state
        done = False
        topos = []
        while not done:
            # Keep requesting topologies until the returned list is empty
            params = {"offset": offset}
            response = self.clnt.get("/topologies", params=params)
            # Get the new topos from this response
            new_topos = response.json().get("result", [])
            if not new_topos:
                # If no new topos returned, we are done
                done = True
                continue
            # Add the newly found user topo to the master user topo list
            topos.extend(new_topos)
            # Adjust the offset to the next page
            offset += response.json().get("pageSize")
        return topos

    def read_user_topologies(self, user):
        """Read a topologies created by provided user name.

        :param user: user of the topologies to read.
        :return: dict of topology information.
        Example response - {...}
        """
        all_topos = self.read_topologies()
        user_topos = []
        for topo in all_topos:
            if topo["created_by"] == user:
                user_topos.append(topo)
        return user_topos

    def read_topology_by_name(self, name):
        """Read a topology by name.

        :param name: name of topology to read.
        :return: dict of topology information.
        Example response - {...}
        """
        all_topos = self.read_topologies()
        for topo in all_topos:
            if topo["name"] == name:
                return topo
        return None

    def read_topology_by_file(self, file_name):
        """Read a topology by file name.

        :param file_name: file name of topology to read.
        :return: dict of topology information.
        Example response - {...}
        """
        all_topos = self.read_topologies()
        for topo in all_topos:
            if topo["file"] == file_name:
                return topo
        return None

    def delete_topology(self, topology_definition_id=None):
        """Delete a topology.

        :param topology_definition_id: ID of topology definition to delete.
        :param name: name of topology definition to delete.
        :param file: file of topology definition to delete.
        :return: dict of response/results.
        Example response - {...}
        """
        if not topology_definition_id:
            raise ACTRESTAPIError("A 'topology_definition_id' must be provided")
        response = self.clnt.delete(f"/topologies/{topology_definition_id}")
        return response.json()

    def read_lab(self, lab_id):
        """Read a lab by ID.

        :param lab_id: ID of lab to get information for.
        :return: dict of lab information.
        Example response - {...}
        """
        # Read a lab by lab ID
        # XXX not working - failing with a read timeout?

        if not lab_id:
            raise ACTRESTAPIError("A valid 'lab_id' must be provided")
        response = self.clnt.get(f"/labs/{lab_id}")
        return response.json()

    def read_labs(self):
        """Read all labs.

        :return: dict of all labs information.
        Example response - {...}
        """
        # Initialize the offset
        offset = 0
        # Initialize done state
        done = False
        # Initialize the labs list
        labs = []
        while not done:
            # Keep requesting labs until the returned list is empty
            params = {"offset": offset}
            response = self.clnt.get("/labs", params=params)
            # Get the new labs from this response
            new_labs = response.json().get("result", [])
            if not new_labs:
                # If no new labs returned, we are done
                done = True
                continue
            labs.extend(new_labs)
            # Adjust the offset to the next page
            offset += response.json().get("pageSize")
        return labs

    def read_users_labs(self, user):
        """Read all labs for provided user.

        :return: dict of all labs information.
        Example response - {...}
        """
        if not user:
            raise ACTRESTAPIError("A valid 'user' must be provided")
        all_labs = self.read_labs()
        user_labs = []
        for lab in all_labs:
            # Filter out the labs that belong to the named user
            # api sets the username of created labs to the email address, not the username
            # so we will match on either <username> or <username>@arista.com
            if lab["user"] == user | lab["user"] == f"{user}@arista.com":
                user_labs.append(lab)
        return user_labs

    def read_lab_by_name(self, name):
        """Read a lab by name.

        :param name: name of lab to get information for.
        :return: dict of lab information.
        Example response - {...}
        """
        if not name:
            raise ACTRESTAPIError("A valid 'name' must be provided")
        all_labs = self.read_labs()
        for lab in all_labs:
            if lab["name"] == name:
                return lab
        return None

    def create_lab(self, name=None, description="", topo_def=None):
        """Create a lab.

        :param name: ID of lab to delete.
        :param description: ...
        :param topo_def: ...
        :return: dict of response/results.
        Example response - {...}
        """
        # Fail if the inputs are not given
        if not name:
            raise ACTRESTAPIError("A 'name' for the lab must be provided")
        if not topo_def:
            raise ACTRESTAPIError("A topolofy definition 'topo_def' for the lab must be provided")
        data = {"name": name, "description": description, "topology_definition": topo_def}
        response = self.clnt.post("/labs", data=data)
        return response.json()

    def delete_lab(self, lab_id):
        """Delete a lab by ID.

        :param lab_id: ID of lab to delete.
        :return: dict of response/results.
        Example response - {...}
        """
        if not lab_id:
            raise ACTRESTAPIError("A valid 'lab_id' must be provided")
        response = self.clnt.delete(f"/labs/{lab_id}")
        return response.json()

    def deploy_lab(self, lab_id):
        """Deploy an existing lab by ID.

        :param lab_id: ID of lab to deploy.
        :return: dict of response/results.
        Example response - {...}
        """
        # Deploy a lab by lab ID
        #   states:
        #       0 - undeployed
        #       1 - undeploying
        #       5 - deploying
        #       12 - configuring
        #       12 - running
        if not lab_id:
            raise ACTRESTAPIError("A valid 'lab_id' must be provided")
        response = self.clnt.post(f"/labs/{lab_id}/deploy")
        return response.json()

    def undeploy_lab(self, lab_id):
        """Undeploy an existing lab by ID.

        :param lab_id: ID of lab to undeploy.
        :return: dict of response/results.
        Example response - {...}
        """
        if not lab_id:
            raise ACTRESTAPIError("A valid 'lab_id' must be provided")
        response = self.clnt.post(f"/labs/{lab_id}/undeploy")
        return response.json()

    def start_lab(self, lab_id):
        """Start an existing lab by ID.

        :param lab_id: ID of lab to start.
        :return: dict of response/results.
        Example response - {...}
        """
        if not lab_id:
            raise ACTRESTAPIError("A valid 'lab_id' must be provided")
        response = self.clnt.post(f"/labs/{lab_id}/start")
        return response.json()

    def stop_lab(self, lab_id):
        """Stop an existing lab by ID.

        :param lab_id: ID of lab to stop.
        :return: dict of response/results.
        Example response - {...}
        """
        if not lab_id:
            raise ACTRESTAPIError("A valid 'lab_id' must be provided")
        response = self.clnt.post(f"/labs/{lab_id}/stop")
        return response.json()
