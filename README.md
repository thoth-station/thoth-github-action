# Thoth Adviser GitHub Action

Get Thoth security guidance on your Python project dependencies.

## Usage

The Thoth Adviser GitHub Action is meant to be used within a CI workflow to detect potential security vulnerabilities in the project dependencies.
The example below shows a basic usage of the action within a workflow (created under the `.github/workflows/` directory) triggered on a `push` event on the repository:

```
name: Your CI workflow
on:
  push:
    paths:
      - 'Pipfile'
jobs:
  validate-dependencies:
    runs-on: ubuntu-latest
    container: quay.io/thoth-station/s2i-thoth-ubi8-py38:latest
    name: Get Thoth recommendations on your dependencies
    steps:
      - uses: actions/checkout@v3
      - name: Get Thoth security recommendations
        id: thoth-advise
        uses: thoth-station/thoth-github-action@v1
        with:
          requirements-path: 'Pipfile'
          requirements-format: pipenv
```

This action should be configured to run on a push event if the requirements file specifying a project dependencies has been modified by the current pull request or commit. In the `on.push.paths` field, specify the path of the requirements file in the repository (supported formats are `Pipfile`, `requirements.txt` and `setup.cfg`).

The `thoth-github-action` should be run using a `s2i-thoth` container image such as `quay.io/thoth-station/s2i-thoth-ubi8-py38:latest` as stated in the example workflow file above. These container images contain a ready-to-use Python environment with pre-installed packages necessary to get Thoth advise on the repository dependencies. For more information on Thoth container images, see the [s2i-thoth repository](https://github.com/thoth-station/s2i-thoth#s2i-thoth).
Before running the action, steps should include checking out the current repository with `actions/checkout@v3`.

The `requirements-path` input parameter representing the path to the dependency requirements file is required to run the `thoth-github-action`, as well as the `requirements-format` parameter to specify the format of your dependencies requirements (one of `pip`, `pip-tools`, `pip-compile` or `pipenv`).

The workflow succeeds if the specified dependencies could be properly resolved and fails if security issues or incompatibilities between dependencies are preventing the resolution, producing an error message and and blocking the Pull Request merge if configured to do so.

### Analyze your dependencies against a specific runtime environment

To analyze dependencies in a given runtime environment, it is possible to configure a project repository to use overlays for each environment dependencies should be analyzed in.
The Thoth configuration file named `.thoth.yaml` should be created at the root of the repository, stating the desired runtime environments to use for the resolution as explained in the [Thoth command line interface documentation](https://github.com/thoth-station/thamos#using-custom-configuration-file-template).

To get advise on multiple runtime environments and store dependency requirement files separately for each environment, it is possible to create [an `overlays` directory](https://github.com/thoth-station/thamos#overlays-directory) in the target repository. A separate workflow to analyze dependencies should then be created for each runtime environment defined in an overlays subdirectory. For example, if the environments you wish to analyze your dependencies against are:

* `fedora` in version `35` using `python 3.10`
* `rhel` in version `8` using `python 3.8`

Under the `.github/workflows/` directory, the different workflow files created would be:


`thoth_dependency_analysis_fedora35.yaml`:

```
name: Analyzing dependencies for fedora 35 and pythonn 3.10
on:
  push:
    paths:
      - 'Pipfile'
jobs:
  validate-dependencies:
    runs-on: ubuntu-latest
    container: quay.io/thoth-station/s2i-thoth-ubi8-py38:latest
    name: Get Thoth recommendations on your dependencies
    steps:
      - uses: actions/checkout@v3
      - name: Get Thoth security recommendations
        id: thoth-advise
        uses: thoth-station/thoth-github-action@v1
        with:
          requirements-path: 'Pipfile'
          requirements-format: pipenv
          overlay-directory: fedora-35
```



`thoth_dependency_analysis_rhel8.yaml`:

```
name: Analyzing dependencies for rhel 8 and pythonn 3.8
on:
  push:
    paths:
      - 'Pipfile'
jobs:
  validate-dependencies:
    runs-on: ubuntu-latest
    container: quay.io/thoth-station/s2i-thoth-ubi8-py38:latest
    name: Get Thoth recommendations on your dependencies
    steps:
      - uses: actions/checkout@v3
      - name: Get Thoth security recommendations
        id: thoth-advise
        uses: thoth-station/thoth-github-action@v1
        with:
          requirements-path: 'Pipfile'
          requirements-format: pipenv
          overlay-directory: rhel-8
```


And the repository directory structure:


```
.
├── project.py
├── overlays
│   ├── fedora-35
│   │   ├── Pipfile
│   │   ├── Pipfile.lock
│   │   ├── .env
│   │   └── constraints.txt
│   └── rhel-8
│   │   ├── Pipfile
│   │   ├── Pipfile.lock
│   │   ├── .env
│   │   └── constraints.txt
└── .thoth.yaml
```

Note that the `overlay-directory` parameter specified and the name of the corresponding overlays subdirectory must be the same.

#### Environments supported by Thoth

The list of environments currently supported by Thoth for dependency recommendations can be found by installing the [thamos command line interface](https://github.com/thoth-station/thamos/tree/master#thamos) and running:

```
thamos environments
```


### Integrating Thoth into a CI workflow

When the Action is triggered on any push event, it is possible to block the merge of the Pull Request concerned in case of workflow failure.
To do so, navigate to your repository `Settings` and go to the `Branches` section.

![](images/settings_branches.png)

Specify a pattern and rules to follow for branches you want to protect from unchecked merges in the `Branch protection rule` section. This will prevent branches with a name matching the pattern and pull requests not conforming to the rules specified to be merged without passing the Action check.

![](images/branch_protection_rule.png)


## Testing the Action locally

It is possible to run a workflow that uses the Thoth Adviser GitHub Action locally with [`act`](https://github.com/nektos/act), without pushing or committing directly to the repository.
You can start using `act` by following the [installation instructions](https://github.com/nektos/act#installation).
Note that `act` requires Docker to be installed and that it does not currently support Podman. If you want to have Docker and Podman simultaneously installed on your system (RHEL8 or CentOS8), you can follow [this tutorial](https://medium.com/faun/how-to-install-simultaneously-docker-and-podman-on-rhel-8-centos-8-cb67412f321e).

When your workflows and actions are ready to be tested, use the [`act` command line interface](https://github.com/nektos/act#example-commands) to trigger the Action locally.
