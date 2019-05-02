DOCKER_RUN = docker-compose run --rm api
black:
    $(DOCKER_RUN) black api tests

isort:
	$(DOCKER_RUN) isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 --recursive --apply api

lint:
    $(MAKE) black
	$(MAKE) isort

test:
    $(DOCKER_RUN) pytest --ignore venv --cov=api --cov=tests --cov-fail-under=80 --cov-report=term-missing
	$(DOCKER_RUN) black  api tests --check
	$(DOCKER_RUN) isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 --recursive --check-only api tests
