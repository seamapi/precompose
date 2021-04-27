#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess
import sys

from typing import List

from precompose.capture import capture_output
from precompose.pack import pack


def check_prequisites() -> None:
    if shutil.which("podman") is None:
        raise RuntimeError("podman not found in PATH")

    if shutil.which("ostree") is None:
        raise RuntimeError("ostree not found in PATH")

    if os.getuid() != 0:
        os.execlp("podman", "podman", "unshare", sys.executable, *sys.argv)


def has_env(key: str):
    if (key in os.environ) and (len(os.environ[key]) > 0):
        return True
    else:
        return False


def parse_argv(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="precompose", description="Import a Docker Compose application into ostree"
    )

    parser.add_argument("ref", metavar="BRANCH", help="ostree branch to commit to")
    parser.add_argument("compose", metavar="COMPOSE", help="path to docker-compose.yml")
    parser.add_argument("--repo", metavar="OSTREE", help="ostree repo to import to")
    parser.add_argument("--sign-by", metavar="KEYID", help="sign commit with GPG key")
    parser.add_argument("--arch", metavar="ARCH", help="architecture to import")
    parser.add_argument("--variant", metavar="VARIANT", help="variant to import")
    args = parser.parse_args(argv)

    if args.arch is None:
        if has_env("PRECOMPOSE_ARCH"):
            args.arch = os.getenv("PRECOMPOSE_ARCH")
        elif has_env("CONTAINER_ARCH"):
            args.arch = os.getenv("CONTAINER_ARCH")

    if args.variant is None:
        if has_env("PRECOMPOSE_VARIANT"):
            args.variant = os.getenv("PRECOMPOSE_VARIANT")
        elif has_env("CONTAINER_VARIANT"):
            args.variant = os.getenv("CONTAINER_VARIANT")

    if args.repo is not None:
        os.environ["OSTREE_REPO"] = args.repo
    elif "OSTREE_REPO" in os.environ:
        args.repo = os.environ["OSTREE_REPO"]

    if args.sign_by is None:
        if "GPG_KEY_ID" in os.environ and len(os.environ["GPG_KEY_ID"]) > 0:
            args.sign_by = os.getenv("GPG_KEY_ID")

    try:
        capture_output("ostree", "refs", suppress_stderr=True)
    except subprocess.CalledProcessError:
        if args.repo is not None:
            capture_output("ostree", f"--repo={args.repo}", "init", "--mode=archive-z2")
            sys.stderr.write(f"NOTICE: initialized ostree repo in {args.repo}\n")
        else:
            raise RuntimeError(
                "Couldn't read ostree repo; try setting OSTREE_REPO or passing --repo."
            )

    return args


def main(argv: List[str] = sys.argv[1:]) -> int:
    try:
        check_prequisites()
        args = parse_argv(argv)
    except Exception as e:
        sys.stderr.write(str(e) + "\n")
        return 1

    commit = pack(**vars(args))
    sys.stderr.write(f"Imported {args.compose} to {args.ref}\n")
    print(commit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
