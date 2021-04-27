export BUILDER_UID := $(shell id -u)
export BUILDER_GID := $(shell id -g)

.PHONY: all
all: wheel

.PHONY: wheel
wheel: sdist
	docker-compose -f builder/docker-compose.yml run --rm manylinux /mnt/builder/build-bdist.sh

.PHONY: sdist
sdist:
	docker-compose -f builder/docker-compose.yml run --rm manylinux /mnt/builder/build-sdist.sh

.PHONY: clean
clean:
	rm -rf __pycache__ .eggs build dist precompose/__pycache__ *.egg-info
