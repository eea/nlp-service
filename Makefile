# TODO: also support fish
SHELL=/bin/bash

PYTHON_VERSION=3.8.10
PROJECT=eea-nlp-service
PIP=~/mambaforge/envs/py38/bin/pip

SOURCE_OBJECTS=app tests

RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

all: help

deploy.requirements:
	poetry export -f requirements.txt -o requirements.txt
	poetry export --dev -f requirements.txt -o requirements-dev.txt

deploy:
	poetry build

format.black:
	poetry run black ${SOURCE_OBJECTS}

format.isort:
	poetry run isort --atomic ${SOURCE_OBJECTS}

format: format.isort format.black

lints.format.check:
	poetry run black --check ${SOURCE_OBJECTS}
	poetry run isort --check-only ${SOURCE_OBJECTS}

lints.flake8:
	git diff --diff-filter=d --name-only origin/development -- '*.py' | xargs poetry run flake8 --ignore=DAR,E203,W503

lints.flake8.strict:
	poetry run flake8

lints.mypy:
	poetry run mypy ${SOURCE_OBJECTS}

lints.pylint:
	poetry run pylint --rcfile pyproject.toml  ${SOURCE_OBJECTS}

lints: lints.flake8

lints.strict: lints lints.pylint lints.flake8.strict lints.mypy

setup: setup.python setup.sysdep.poetry setup.project		## Setup the development environment

condaenv:
	conda activate py38

setup.conda:
	conda install mamba -n base -c conda-forge
	conda create -n py38 python=3.8
	conda init fish
	conda activate py38
	mamba install pytorch cudatoolkit=10.2 tensorflow tensorflow-hub -c pytorch
	pip install poetry
	pip install https://github.com/deepset-ai/haystack/archive/master.zip
	# pip install -e .

setup.uninstall: setup.python
	poetry env remove ${PYTHON_VERSION} || true

setup.ci: setup.ci.poetry setup.project

setup.ci.poetry:
	${PIP} install poetry

setup.project:
	@poetry env use $$(python -c "import sys; print(sys.executable)")
	@echo "Active interpreter path: $$(poetry env info --path)/bin/python"

	poetry install
setup.python.activation:
	@pyenv local ${PYTHON_VERSION} >/dev/null 2>&1 || true
	@asdf local python ${PYTHON_VERSION} >/dev/null 2>&1 || true

setup.python: setup.python.activation
	@echo "Active Python version: $$(python --version)"
	@echo "Base Interpreter path: $$(python -c 'import sys; print(sys.executable)')"
	@test "$$(python --version | cut -d' ' -f2)" = "${PYTHON_VERSION}" \
        || (echo "Please activate python ${PYTHON_VERSION}" && exit 1)

setup.sysdep.poetry:
	@command -v poetry \&> /dev/null \
        || (echo "Poetry not found. \n  Installation instructions: https://python-poetry.org/docs/" \
            && exit 1)

test:
	docker-compose up unit-tests

test.clean:
	docker-compose down
	-docker images -a | grep ${eea-nlp-service} | awk '{print $3}' | xargs docker rmi
	-docker image prune -f

test.shell:
	docker-compose run unit-tests /bin/bash

test.shell.debug:
	docker-compose run --entrypoint /bin/bash unit-tests

test.local: setup
	poetry run coverage run -m pytest

.PHONY: run
start:		## Start the development server
	poetry run uvicorn app.main:app

.PHONY: gtop
gtop:
	sudo fuser -v /dev/nvidia*

.PHONY: help
help:		## Show this help.
	@echo -e "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)"
