import json
import tempfile

from pathlib import Path
from ruamel.yaml import YAML
from typing import Any, Dict, Optional, cast

from holocron.capture import capture_output

yaml = YAML()


def check_services(compose_path: Path, compose_yaml: Any):
    if not isinstance(compose_yaml, dict):
        raise RuntimeError(f"{compose_path} isn't a dict?!?")

    if "services" not in compose_yaml:
        raise RuntimeError(f"no services service in {compose_path}?!?")

    if not isinstance(compose_yaml["services"], dict):
        raise RuntimeError(f"services in {compose_path} isn't a dict?!?")

    services: Dict[Any, Any] = compose_yaml["services"]

    if len(services) < 1:
        raise RuntimeError(f"no services in {compose_path}?!?")

    for service, service_data in services.items():
        if not isinstance(service, str):
            raise RuntimeError("service name is not a string?!?")

        if not isinstance(service_data, dict):
            raise RuntimeError(f"service {service} is not a dict?!?")

        if "image" not in service_data:
            raise RuntimeError(f"no image specified for {service}")


def pull_images(compose_yaml: Any, storage: Path, arch: str, variant: Optional[str]):
    pulls = set([service["image"] for service in compose_yaml["services"].values()])
    images: Dict[str, str] = {}

    pull_args = ["--arch", arch]
    if variant is not None:
        pull_args += ["--variant", variant]

    for pull in pulls:
        images[pull] = capture_output(
            "podman",
            "pull",
            "--root",
            str(storage),
            *pull_args,
            pull,
        )

    return images


def pack(
    ref: str,
    compose: str,
    repo: str,
    sign_by: Optional[str],
    arch: str,
    variant: Optional[str],
) -> str:
    compose_path = Path(compose).absolute()
    with open(compose_path, "r") as compose_in:
        compose_yaml = cast(Any, yaml).load(compose_in)

    check_services(compose_path, compose_yaml)

    with tempfile.TemporaryDirectory() as tempstr:
        tempdir = Path(tempstr)
        storage = tempdir.joinpath("storage")
        storage.mkdir()
        images = pull_images(compose_yaml, storage, arch, variant)

        for service in compose_yaml["services"]:
            image = compose_yaml["services"][service]["image"]
            compose_yaml["services"][service]["image"] = images[image]

        app = tempdir.joinpath(compose_path.parent.name)
        app.mkdir()

        new_compose_path = app.joinpath("docker-compose.yml")
        with open(new_compose_path, "w") as compose_out:
            cast(Any, yaml).dump(compose_yaml, compose_out)

        metadata = tempdir.joinpath("holocron.json")
        with open(metadata, "w") as metadata_out:
            json.dump(
                {"holocron": {"app": app.name, "version": 0, "images": images}},
                metadata_out,
            )

        commit_args = [
            f"--repo={repo}",
            f"--branch={ref}",
            f"--tree=dir={tempdir}",
            f"--subject=holocron of {app.name}",
            f"--body-file={metadata}",
        ]

        if sign_by is not None:
            commit_args.append(f"--gpg-sign={sign_by}")

        commit = capture_output("ostree", "commit", *commit_args)

    return commit
