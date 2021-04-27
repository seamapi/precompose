import json
import shutil
import tempfile

from pathlib import Path
from ruamel.yaml import YAML
from typing import Any, Dict, List, Optional, cast

from holocron.capture import capture_output

yaml = YAML()


def evaluate_config(compose_path: Path):
    return cast(Any, yaml).load(
        capture_output("docker-compose", "-f", str(compose_path), "config")
    )


def check_services(compose_path: Path, compose_yaml: Any):
    if not isinstance(compose_yaml, dict):
        raise RuntimeError(f"{compose_path} isn't a dict?!?")

    if "services" not in compose_yaml:
        raise RuntimeError(f"no services key in {compose_path}?!?")

    if not isinstance(compose_yaml["services"], dict):
        raise RuntimeError(f"services in {compose_path} isn't a dict?!?")

    services: Dict[Any, Any] = compose_yaml["services"]

    if len(services) < 1:
        raise RuntimeError(f"no services defined in {compose_path}?!?")

    for service, service_data in services.items():
        if not isinstance(service, str):
            raise RuntimeError("service name is not a string?!?")

        if not isinstance(service_data, dict):
            raise RuntimeError(f"service {service} is not a dict?!?")

        if "image" not in service_data:
            raise RuntimeError(f"no image specified for {service}")


def qualify_image(image: str) -> str:
    if len(image.split("/")) < 2:
        image = "library/" + image

    if len(image.split("/")) < 3:
        image = "registry-1.docker.io/" + image

    if len(image.split(":")) < 2:
        image += ":latest"

    return image


def pull_images(
    compose_yaml: Any, storage: Path, arch: Optional[str], variant: Optional[str]
):
    pulls = set([service["image"] for service in compose_yaml["services"].values()])
    images: Dict[str, str] = {}
    pull_args: List[str] = []

    if arch is not None:
        pull_args += ["--arch", arch]

    if variant is not None:
        pull_args += ["--variant", variant]

    for pull in pulls:
        qualified = qualify_image(pull)
        basename = qualified.rsplit(":", 1)[0]
        sha256 = capture_output(
            "podman",
            "pull",
            "--root",
            str(storage),
            *pull_args,
            qualified,
        )

        images[pull] = f"{basename}@sha256:{sha256}"

    return images


def pack(
    ref: str,
    compose: str,
    repo: str,
    sign_by: Optional[str],
    arch: Optional[str],
    variant: Optional[str],
) -> str:
    compose_path = Path(compose).absolute()
    compose_config = evaluate_config(compose_path)

    with open(compose_path, "r") as compose_in:
        compose_yaml = cast(Any, yaml).load(compose_in)

    check_services(compose_path, compose_config)

    with tempfile.TemporaryDirectory() as tempstr:
        tempdir = Path(tempstr)
        tempdir.chmod(0o755)

        storage = tempdir.joinpath("storage")
        storage.mkdir()
        images = pull_images(compose_config, storage, arch, variant)
        env_files: List[str] = []

        for name, service in compose_config["services"].items():
            compose_yaml["services"][name]["image"] = images[service["image"]]
            if "env_file" in compose_yaml["services"][name]:
                if isinstance(compose_yaml["services"][name]["env_file"], list):
                    env_files += compose_yaml["services"][name]["env_file"]
                else:
                    env_files.append(service["env_file"])

        app = tempdir.joinpath(compose_path.parent.name)
        app.mkdir()

        new_compose_path = app.joinpath("docker-compose.yml")
        with open(new_compose_path, "w") as compose_out:
            cast(Any, yaml).dump(compose_yaml, compose_out)

        for env_file in env_files:
            shutil.copyfile(
                compose_path.parent.joinpath(env_file), app.joinpath(env_file)
            )

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
