# type: ignore

import setuptools

setuptools.setup(
    name="holocron",
    version="0.1.0",
    author="Seam",
    author_email="hello@getseam.com",
    description="holocron imports Docker Compose applications into ostree",
    url="https://github.com/hello-seam/holocron",
    packages=["holocron"],
    python_requires=">=3.8",
    license="AGPL-3.0-or-later",
    entry_points={"console_scripts": ["holocron=holocron.main:main"]},
)
