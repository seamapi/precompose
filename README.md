# holocron

`holocron` is a tool to import a [Compose](https://www.compose-spec.io/) application into an [OSTree](https://ostreedev.github.io/ostree/introduction/) repository.

Distributing container images through an OSTree repository has some advantages, compared to the use of a container registry:

- Images are deduplicated at the file level with OSTree, instead of at the layer level.
- If your host is also managed by OSTree and is based on the same OS as your containers, then images are also deduplicated at the file level against the host.
- Updates are done at the file level, instead of at the layer level - this can save significant amounts of bandwidth when only one or a few files in a layer have changed.

`holocron` produces an OSTree commit which contains:

- Your original `docker-compose.yml`, rewritten to pin each image to a specific SHA
- Any `env_file` referenced by your `docker-compose.yml`
- A directory containing exploded copies of all the containers your application needs, which can be used as an [additional image store](https://www.redhat.com/sysadmin/image-stores-podman) with [Podman](https://podmain.io)

## Requirements

In addition to the Python modules that it requires, `holocron` also needs some external tools to do its work:

### [Docker Compose](https://github.com/docker/compose)

`holocron` actually does depend on this as a Python module, but only uses it as an external tool, since it does not have a stable API. It is used to preprocess the Compose file and interpolate any environment variables that may be present in the image name.

`docker-compose` is also needed to run an application packaged with `holocron`.

### [OSTree](https://github.com/ostreedev/ostree)

`holocron` shells out to the `ostree` command-line tool in order to create its commits.

### [Podman](https://github.com/containers/podman)

`holocron` shells out to `podman unshare` to simulate being root and to `podman pull --root` to pull container images.

Your system must be configured in a way that `podman` can operate without root privileges (aka "rootless containers") - on most Debian and Ubuntu based systems, installing the `uidmap` package along with Podman should be enough. Your mileage may vary.

`podman` is also needed to run an application packaged with `holocron`, since Docker does not have anything equivalent to an additional image store. It is strongly recommended to use version 3.0 or later of Podman; the APIs used by `docker-compose` are incomplete in earlier versions.

## Usage

```
holocron [-h] [--repo OSTREE] [--sign-by KEYID] [--arch ARCH] [--variant VARIANT] BRANCH COMPOSE

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
