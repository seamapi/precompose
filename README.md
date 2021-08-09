# precompose

`precompose` is a tool to import a [Compose](https://www.compose-spec.io/) application into an [OSTree](https://ostreedev.github.io/ostree/introduction/) repository.

Distributing container images through an OSTree repository has some advantages, compared to the use of a container registry:

- Images are deduplicated at the file level with OSTree, instead of at the layer level.
- If your host is also managed by OSTree and is based on the same OS as your containers, then images are also deduplicated at the file level against the host.
- Updates are done at the file level, instead of at the layer level - this can save significant amounts of bandwidth when only one or a few files in a layer have changed.

`precompose` produces an OSTree commit which contains:

- Your original `docker-compose.yml`, rewritten to pin each image to a specific SHA
- A directory containing exploded copies of all the containers your application needs, which can be used as an [additional image store](https://www.redhat.com/sysadmin/image-stores-podman) with [Podman](https://podmain.io)

## Requirements

In addition to the Python modules that it requires, `precompose` also needs some external tools to do its work:

### [Docker Compose](https://github.com/docker/compose)

While `docker-compose` can be installed from PyPI, `precompose` only uses it as an external tool, since it does not have a stable API. Because it is not used as a library, and because you may have obtained `docker-compose` from a place other than PyPI, it is not declared as a Python dependency of this module. It is used to preprocess the Compose file and interpolate any environment variables that may be present in the image name.

`docker-compose` is also needed to run an application packaged with `precompose`.

### [OSTree](https://github.com/ostreedev/ostree)

`precompose` shells out to the `ostree` command-line tool in order to create its commits.

### [Podman](https://github.com/containers/podman)

`precompose` shells out to `podman unshare` to simulate being root and to `podman pull --root` to pull container images.

Your system must be configured in a way that `podman` can operate without root privileges (aka "rootless containers") - on most Debian and Ubuntu based systems, installing the `uidmap` package along with Podman should be enough. Your mileage may vary.

`podman` is also needed to run an application packaged with `precompose`, since Docker does not have anything equivalent to an additional image store. It is strongly recommended to use version 3.0 or later of Podman; the APIs used by `docker-compose` are incomplete in earlier versions.

## Installation

Install using pip:

```bash
pip3 install precompose
```

...or, grab the latest release from [GitHub](https://github.com/hello-seam/precompose/releases) or [PyPI](https://pypi.org/project/precompose/) and install it manually.

## Usage

```
precompose [-h] [--repo OSTREE] [--sign-by KEYID] [--arch ARCH] [--variant VARIANT] BRANCH COMPOSE

Import a Docker Compose application into ostree

positional arguments:
  BRANCH             ostree branch to commit to
  COMPOSE            path to docker-compose.yml

optional arguments:
  -h, --help         show this help message and exit
  --repo OSTREE      ostree repo to import to
  --sign-by KEYID    sign commit with GPG key
  --arch ARCH        architecture to import
  --variant VARIANT  variant to import
```

## Utilities

`precompose_utils` (on [GitHub](https://github.com/hello-seam/precompose_utils) and [PyPI](https://pypi.org/project/precompose-utils/)) contains a set of utilties for working with applications that have been packaged with `precompose`.
