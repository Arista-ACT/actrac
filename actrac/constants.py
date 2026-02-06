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

"""ACT REST API Client Constants."""

ACT_REST_API_PATH = "/rest/v1"

OPERATIONS_VALID_STATES = {
    "start_lab": ["Stopped", "Running", "Pending", "Starting"],
    "stop_lab": ["Stopped", "Pending", "Stopping", "Running"],
    "deploy_lab": [
        "Ready",
        "Running",
        "Pending",
        "Starting",
        "Deploying",
        "Job Created",
        "Configuring",
        "Stopped",
    ],
    "undeploy_lab": ["Ready", "Running", "Pending", "Starting", "Undeploying", "Stopped"],
}


class LAB_STATES:
    """LAB STATES ENUM."""

    READY = 0
    PENDING = 1
    RUNNING = 2
    STOPPING = 3
    STOPPED = 4
    DEPLOYING = 5
    UNDEPLOYING = 6
    REBOOTING = 7
    STARTING = 8
    FAILED = 9
    DEPLOYMENT_FAILED = 10
    NODE_QUOTA_REACHED = 11
    CONFIGURING = 12


LAB_STATE_STR_TO_INT_MAP = {
    "Ready": LAB_STATES.READY,
    "Pending": LAB_STATES.PENDING,
    "Running": LAB_STATES.RUNNING,
    "Stopping": LAB_STATES.STOPPING,
    "Stopped": LAB_STATES.STOPPED,
    "Deploying": LAB_STATES.DEPLOYING,
    "Undeploying": LAB_STATES.UNDEPLOYING,
    "Rebooting": LAB_STATES.REBOOTING,
    "Starting": LAB_STATES.STARTING,
    "Failed": LAB_STATES.FAILED,
    "DeploymentFailed": LAB_STATES.DEPLOYMENT_FAILED,
    "NodeQuotaReached": LAB_STATES.NODE_QUOTA_REACHED,
    "Configuring": LAB_STATES.CONFIGURING,
}
