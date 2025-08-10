# -------------------------------------------------------------------------------------------
# VARIABLES: Variable declarations to be used within make to generate commands.
# -------------------------------------------------------------------------------------------
# Variables that are specific to each project.
PROJECT      := nautobot-mcp-server
REPO         := mcp
REGISTRY     := local
VERSION      := $(shell poetry version --short)
NAUTOBOT_VER := $(shell grep '^nautobot = ' pyproject.toml | sed 's/nautobot = "\([^"]*\)"/\1/')
COVERAGE_PCT := 50

# These variables should be the same
VARIABLES := VERSION=$(VERSION) NAUTOBOT_VER=$(NAUTOBOT_VER) REPO=$(REPO) REGISTRY=$(REGISTRY)
BAKE = $(VARIABLES) docker buildx bake "--allow=fs.read=.." -f "docker-compose.yml"
BASE = $(VARIABLES) docker compose --project-name $(PROJECT) --project-directory "development" -f "development/docker-compose.yml"
DOCS = $(VARIABLES) docker compose --project-name $(PROJECT) --project-directory "development" -f "development/docker-compose.docs.yml"

default: help

cli: .env ## Exec into an already running Nautobot container. Start the container if stopped.
ifeq (,$(findstring nautobot,$($BASE ps --services --filter status=running)))
	@make start
endif
	@$(BASE) exec nautobot bash
.PHONY: cli

debug: .env ## Launch docker-compose environment in attached mode. Use `make debug agg` to launch aggregate instance as well.
	@$(BASE) up
.PHONY: debug

docs: .env ## Deploy the documentations site locally for testing.
	@$(DOCS) up
.PHONY: docs

logs: .env ## Tail the logs of the compose environment.
	@$(BASE) logs -f --tail=500
.PHONY: logs

start: .env ## Start the docker-compose environment in detached mode. Use `make debug agg` to launch aggregate instance as well.
	@ENV=local $(BASE) up -d
.PHONY: start

stop: ## Stop and bring down all the running containers started by compose.
	@$(BASE) down
.PHONY: stop

createsuperuser: .env ## Create the Nautobot superuser.
ifeq (,$(findstring nautobot,$($BASE ps --services --filter status=running)))
	@make start
endif
	@$(BASE) exec nautobot nautobot-server createsuperuser
.PHONY: createsuperuser

restart: .env ## Restart docker containers.
	@$(BASE) restart
.PHONY: restart

destroy: ## Destroy all the docker containers and attached volumes. This will delete all data!!
	@$(BASE) down --volumes
.PHONY: destroy

shell: .env ## Exec into the Nautobot container and start the `shell_plus` environment.
ifeq (,$(findstring nautobot,$($BASE ps --services --filter status=running)))
	@make start
endif
	@$(BASE) exec nautobot nautobot-server shell_plus
.PHONY: shell

# -------------------------------------------------------------------------------------------
# CODE QUALITY: Running linting and security checks
# -------------------------------------------------------------------------------------------
tests: lint unittest ## Runs both code linting and unit tests in the dev container.
.PHONY: tests

lint: .env poetry-lock ## Runs code quality tests in the poetry env.
	@make -s _ruff_lint
	@echo "✅ All linting processes complete! 🎉"
.PHONY: lint

lint-fix: .env poetry-lock ## Runs code formatting and fixes linting issues in the poetry env.
	@make -s _ruff_lint_fix
	@echo "✅ All linting fixes applied! 🎉"
.PHONY: lint-fix

_ruff_lint:
	@echo "🔍 Running Python Ruff Linting... 🔍"
	@poetry run ruff format . --check --diff
	@poetry run ruff check .
.PHONY: _ruff_lint

_ruff_lint_fix:
	@echo "🔧 Running Python Ruff Linting with Auto-Fix... 🔧"
	@poetry run ruff format .
	@poetry run ruff check . --fix
.PHONY: _ruff_lint_fix

unittest: .env _unittest ## Runs unit tests in the poetry virtual env.
.PHONY: unittest

_unittest:
	@echo "🧪 Running PyTest with Coverage... 🧪"
	@poetry run pytest tests/ --cov=nautobot_mcp_server --cov-report=html --cov-report=term-missing --cov-fail-under=${COVERAGE_PCT} -v
.PHONY: _unittest

install: .env ## Install the Nautobot development environment.
	@echo "Installing Nautobot development environment..."
	@poetry install --with dev


# -------------------------------------------------------------------------------------------
# DOCKER/BUILD: Building of containers and pushing to registries
# -------------------------------------------------------------------------------------------
build:  ## Builds a new development container. Does not use cached data.
	@cd development && $(BAKE) --no-cache nautobot
.PHONY: build

#push:  ## Push the built image to the AWS ECR repository.
#	@echo "Pushing Nautobot image to AWS ECR..."
#	@cd development && $(BAKE) --push nautobot


# -------------------------------------------------------------------------------------------
# GENERAL: utility commands for environment management.
# -------------------------------------------------------------------------------------------
poetry-lock:
	@if [ ! -f "${PWD}/poetry.lock" ]; then \
	   echo "Running poetry lock..."; \
	   poetry lock; \
	fi
.PHONY: poetry-lock

.env:
	@if [ ! -f "${PWD}/development/.env" ]; then \
	   echo "Creating environment file..."; \
	   cp ${PWD}/development/.env.example ${PWD}/development/.env; \
	fi
.PHONY: .env

_env-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		echo "Please check README.md or Makefile for variables required."; \
		echo "(╯°□°）╯︵ ┻━┻"; \
		exit 1; \
	fi
.PHONY: _env-%

help:
	@echo "\033[1m\033[01;32m\
	$(shell echo $(PROJECT) | tr  '[:lower:]' '[:upper:]') $(VERSION) \
	\033[00m\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' \
	$(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; \
	{printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help

%::
	@true
