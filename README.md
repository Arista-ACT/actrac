# ACT Restful API Client (ACTRAC) Library

## Table of Contents

1. [Overview](#overview)
    - [Requirements](#requirements)
1. [Installation](#installation)
    - [Development: Run from Source](#development-run-from-source)
1. [Getting Started](#getting-started)
    - [Connecting](#connecting)
    - [Examples](#examples)
1. [Notes](#notes)
1. [Testing](#testing)
1. [Contact or Questions](#contact-or-questions)
1. [Contributing](#contributing)
    - [Working With Git](#working-with-git)
    - [Submitting Pull Requests](#submitting-pull-requests)
    - [Pull Request Semantics](#pull-request-semantics)
1. [License](#license)

## Overview

This module provides a Python client for interfacing with the ACT REST API.
This can be used for spinning up (deploying/starting) ACT environments to run tests against
and then spinning them down (undeploying/stopping) after the tests have completed.

### Requirements

- Python 3.10 or later
- Poetry 1.3.1 or later (required to run from source)

## Installation


### Installing Package

The library is published as a python pacakge on PyPi and installable via pip.

### Development: Run from Source

You can also run the ACTRAC library in a Python Poetry virtual
environment. For more information, read this:
<https://python-poetry.org/docs/>

These instructions will help you install and run the ACTRAC library
from source. This is useful if you plan on contributing or if you would always
like to see the latest code in the develop branch. Note that these steps
require the poetry and git commands.

#### Pre-Requisite: Download and Install Poetry

    <https://python-poetry.org/docs/#installation>

#### Step 1: Clone the ACTRAC library from Github repo

    # Go to a directory where you'd like to keep the source
    admin:~ admin$ cd ~/projects
    admin:~ admin$ git clone https://github.com/Arista-ACT/ACTRAC.git
    admin:~ admin$ cd actrac

#### Step 2: Check out the desired version or branch

    # Go to a directory where you'd like to keep the source
    admin:~ admin$ cd ~/projects/actrac

    # To see a list of available versions or branches
    admin:~ admin$ git tag
    admin:~ admin$ git branch

    # Checkout the desired version of code
    admin:~ admin$ git checkout v0.2.0

#### Step 3: Install actrac library using Poetry

    # Go to a directory where you'd like to keep the source
    admin:~ admin$ cd ~/projects/actrac

    # Install
    admin:~ admin$ poetry install

#### Step 4: Install ACTRAC library development requirements

    No different from standard poetry install currently.

## Getting Started

Once the package has been installed you can run the following example to
verify that everything has been installed properly.

    # Run UnitTests
    admin:~ admin$ make unittest

### Connecting

Connecting to ACT will depend on what Tenant you have access to. You will have
to make sure you are connected to the appropriate VPN using an OVPN client and
profile before running any scripts that will interact with the ACT API.

### OVPN

Connect using OpenVPN Client using the appropriate profile.

### API KEY

To use the ACT API you will need to generate an API KEY for authenticating the API requests.
Generate this key using the ACT UI after logging in using existing ACT credentials.

### Examples

Example connecting to the ACT API and getting all available versions:

    >>> from actrac.client import ACTClient
    >>> client = ACTClient(api_key="EXAMPLE", base_url="https://lab.act.arista.com", log_stdout=True)
    >>> client.connect(username, password)
    >>> result = client.api.available_node_versions()
    >>> print result
    {...large output omitted...}
    >>>

Example connecting to the ACT API and getting all available versions for a HTTPS Tenant ():

    >>> from actrac.client import ACTClient
    >>> client = ACTClient(api_key="EXAMPLE", base_url="https://<tenant identifier>.act.arista.com", log_stdout=True)
    >>> client.connect(username, password)
    >>> result = client.api.available_node_versions()
    >>> print result
    {...large output omitted...}
    >>>

Example connecting to the ACT API and getting all labs:

    >>> from actrac.client import ACTClient
    >>> client = ACTClient(api_key="EXAMPLE", base_url="lab.act.arista.com", log_stdout=True)
    >>> client.connect(username, password)
    >>> result = client.api.read_labs()
    >>> print result
    {...large output omitted...}
    >>>

Example connecting to the ACT API and attempting to start a lab and wait for it to be running:

    >>> from actrac.client import ACTClient
    >>> client = ACTClient(api_key="EXAMPLE", base_url="lab.act.arista.com", log_stdout=True)
    >>> client.connect(username, password)
    >>> result = client.api.read_lab_by_name("EXAMPLE LAB")
    >>> lab_id = result["lab_id"]
    >>> print("START DEPLOY WAIT FOR RUNNING\n")
    >>> client.loop.run_until_complete(client.api.deploy_lab_wait_for_running(lab_id))
    {...}
    >>>

## Notes

...

## Testing

Currently there are a couple of example scripts in the ./examples directory that can be used
to verify interaction with your ACT Tenant via ACTRAC.

There are also unittests for the client that are maintained by the ACT development team.

Additionally any external contribution must containe appropriate unittests.

## Contact or Questions

The ACTRAC Library is developed by Arista ACT Team and supported
by the Arista ACT community. You can contact the team that
develops these modules by sending an email to <act-dev@arista.com>.

For customers that are looking for a premium level of support, please
contact your local account team or email <act-dev@arista.com> for help.

## Contributing

Contributing pull requests are gladly welcomed for this repository.
Not only contributing to the code but also we encourage the users to contribute
in the form of examples, docs, tutorials, and user guides.

Please note that all contributions that modify the library behavior
require corresponding test cases otherwise the pull request will be
rejected.

### Working With Git

It is recommended to fork the project and then start development on the forked repository's **develop** branch. This can achieved with the below steps:

- Info...

- Create a new feature branch (off the develop branch) to contain your feature, change, or fix:

       git checkout -b <feature-branch-name>

- OPTIONAL: Install pre-commit checks. This will trigger linting and unit tests on every git commit, so that any issues are identified locally. This is optional but it may help to catch issues early.

        `pre-commit install`

- Commit your changes in logical chunks. Please adhere to these [git commit
   message guidelines](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)
   or your code is unlikely to be merged into the main project. Use Git's
   [git rebase](https://docs.github.com/en/get-started/using-git/about-git-rebase)
   feature to tidy up your commits before making them public.

- Locally merge (or rebase) the upstream development branch into your feature branch every time before pushing it to your fork:

        # Here the <dev-branch> is develop
        git pull [--rebase] upstream <dev-branch>

- Push your feature branch up to your fork:

        git push origin <feature-branch-name>

- [Open a Pull Request]()
    with a clear title, description and explain how to test the feature.

### Submitting Pull Requests

- It is recommended to open an issue before starting work on a pull request to make sure if the same issue is not reported previously and someone is already working on that. When suggesting a new feature, also make sure it won't conflict with any work that's already in progress.

- Once the issue is opened either self-assign the issue or ask the maintainer to assign it for you. This will make sure no others are working on the same issue.

- All new functionality must include relevant tests where applicable.

- When submitting a pull request, please be sure to work off of the **develop** branch and not from other branches. The **develop** branch is used for ongoing development, while the **master** will hold the last stable version.

- To automate release-notes creation and make filtering process easier, it is strongly recommended to use [conventional commit](https://www.conventionalcommits.org/en/v1.0.0/#summary) syntax at least for Pull Request (PR) title.

- All code submissions must follow the below criteria:

  - The issue/PR title should follow the semantic as described [here](#pull-request-semantics)
  - All the tests are updated and are passed successfully
  - Python syntax is valid

### Pull Request Semantics

The Pull Request title should start with one of the below to easily segregate if
its a feature add or a bug or something related documentation etc.

It is strongly recommended to use one from the below:

- ```Feat```: Create a capability e.g. feature, test, dependency
- ```Fix```: Fix an issue e.g. bug, typo, accident, misstatement
- ```Doc```: Refactor of documentation, e.g. help files
- ```Example```: Add a new example or modify an [existing one](docs/labs/)
- ```Test```: Add or refactor anything regarding test, e.g add a new testCases or missing testCases
- ```Refactor```: A code change that MUST be just a refactoring
- ```Bump```: Increase the version of something e.g. dependency
- ```Revert```: Change back to the previous commit
- ```Optimize```: Refactor of performance, e.g. speed up code
- ```CI```: Update CI components, e.g. molecule files or Github Actions
- ```Cut```: Remove a capability e.g. feature, test, dependency

For example:

- Feat: Add support for decommissioning APIs
- Test: Add missing test cases for message sending
- Doc: Document new examples for new message handling

## License

Copyright© 2026, Arista Networks, Inc. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

- Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
- Neither the name of Arista Networks nor the names of its
    contributors may be used to endorse or promote products derived from
    this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS \"AS
IS\" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
THE POSSIBILITY OF SUCH DAMAGE.
