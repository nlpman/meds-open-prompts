.SECONDARY:

PACKAGE := medsop
IMAGE_NAME := meds_open_prompts
PYTHON_VERSION := 3.10
VERSION := $(shell sed -n 's/^ *version.*=.*"\([^"]*\)".*/\1/p' pyproject.toml)


format:
	poetry run isort $(PACKAGE)
	poetry run autoflake -r --in-place --remove-unused-variables $(PACKAGE)
	poetry run black $(PACKAGE)
	poetry run black tests

type_check: format
	poetry run python -m mypy --python-version $(PYTHON_VERSION) $(PACKAGE)
	poetry run python -m mypy --python-version $(PYTHON_VERSION) tests --check-untyped-defs

test: type_check
	poetry run coverage run --source $(PACKAGE) -m pytest -v -m "not training" --tb=line --show-capture=all tests 
	poetry run coverage report -m

docker-build: test
	docker build -t $(IMAGE_NAME):$(VERSION) .

split_training:
	poetry run python $(PACKAGE)/drug_reviews.py split-training-for-annotation

#docker_compose_start_mongo_only:
#	docker compose up mongo

#mongo_restore_to_docker_compose:
#	mongorestore --host 127.0.0.1 --port 27016

#mongo_connect_docker_compose:
#	mongo --host 127.0.0.1 --port 27016

