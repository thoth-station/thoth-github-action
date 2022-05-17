# Thoth Adviser GitHub Action

Get Thoth security guidance on your Python project dependencies.

## Usage

```
name: Your CI workflow
on:
  push:
    paths:
      - 'requirements.txt'
      - 'Pipfile'
jobs:
  validate-dependencies:
    runs-on: ubuntu-latest
    container: quay.io/thoth-station/s2i-thoth-ubi8-py38:latest
    name: Get Thoth recommenations on your dependencies
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Get Thoth security advisories
        id: thoth-advise
        uses: thoth-station/thoth-github-action@v1
        with:
          requirements-path: 'Pipfile'
          requirements-format: pipenv
```

This action should be configured to run on a push event if the requirements file specifying a project dependencies has been modified by the current pull request or commit. In the `on.push.paths` field, specify the path of the requirements file in the repository (supported formats are `Pipfile` or `requirements.txt`).

Before running the `thoth-github-action`, steps should include checking out the current repository with `actions/checkout@v3` and setting up a Python environment with
```
- uses: actions/setup-python@v2
  with:
    python-version: 3.8
```

The `requirements-path` input parameter representing the path to the requirements file is required to run `thoth-github-action`, as well as the `requirements-format` parameter to specify the format of your dependencies requirements (one of (pip | pip-tools | pip-compile | pipenv)).

The workflow succeeds if the specified dependencies could be properly resolved and fails if security issues or incompatibilities are preventing the resolution, producing an error message and and blocking the CI if configured to do so.

### Integrating Thoth into a CI workflow

When the Action is triggered on any push event, it is possible to block the pull request concerned in case of workflow failure.
To do so, navigate to your repository `Settings` and go to the `Branches` section.

![](images/settings_branches.png)

Specify a pattern and rules to follow for branches you want to protect from unchecked merges in the `Branch protection rule` section. This will prevent branches with a name matching the pattern and pull requests not conforming to the rules specified to be merged without passing the Action check.

![](images/branch_protection_rule.png)


## Testing the Action locally

You can test the action locally using [`act`](https://github.com/nektos/act) without pushing or committing directly to the repository.
You can follow the installation instructions for `act` [here](https://github.com/nektos/act#installation).
Note that `act` requires Docker to be installed and that it does not currently support Podman. If you want to have Docker and Podman simultaneously installed on your system (RHEL8 or CentOS8), you can follow [this tutorial](https://medium.com/faun/how-to-install-simultaneously-docker-and-podman-on-rhel-8-centos-8-cb67412f321e).

When your workflows and actions are ready to be tested, use the [`act` command line interface](https://github.com/nektos/act#example-commands) to trigger the Action locally.
