.EXPORT_ALL_VARIABLES:
# Get changed files

FILES := $(wildcard **/*.py)

# if you wrap everything in uv run, it runs slower.
ifeq ($(origin VIRTUAL_ENV),undefined)
    VENV := uv run
else
    VENV :=
endif

uv.lock: pyproject.toml
	@echo "Installing dependencies"
	@uv sync

clean-pyc:
	@echo "Removing compiled files"


clean-test:
	@echo "Removing coverage data"
	@rm -f .coverage || true
	@rm -f .coverage.* || true

clean: clean-pyc clean-test

# tests can't be expected to pass if dependencies aren't installed.
# tests are often slow and linting is fast, so run tests on linted code.
test: clean uv.lock install_plugins
	@echo "Running unit tests"
	# $(VENV) pytest --doctest-modules jiggle_version
	# $(VENV) python -m unittest discover
	$(VENV) py.test test -vv -n 2 --cov=jiggle_version --cov-report=html --cov-fail-under 35 --cov-branch --cov-report=xml --junitxml=junit.xml -o junit_family=legacy
	$(VENV) bash basic_checks.sh
#	$(VENV) bash basic_test_with_logging.sh


.build_history:
	@mkdir -p .build_history

.build_history/isort: .build_history $(FILES)
	@echo "Formatting imports"
	$(VENV) isort .
	@touch .build_history/isort

.PHONY: isort
isort: .build_history/isort

.build_history/black: .build_history .build_history/isort $(FILES)
	@echo "Formatting code"
	$(VENV) metametameta pep621
	$(VENV) black jiggle_version # --exclude .venv
	$(VENV) black test # --exclude .venv
	$(VENV) git2md jiggle_version --ignore __init__.py __pycache__ --output SOURCE.md

.PHONY: black
black: .build_history/black

.build_history/pre-commit: .build_history .build_history/isort .build_history/black
	@echo "Pre-commit checks"
	$(VENV) pre-commit run --all-files
	@touch .build_history/pre-commit

.PHONY: pre-commit
pre-commit: .build_history/pre-commit

.build_history/bandit: .build_history $(FILES)
	@echo "Security checks...off"
#	$(VENV)  bandit jiggle_version -r
#	@touch .build_history/bandit

.PHONY: bandit
bandit: .build_history/bandit

.PHONY: pylint
.build_history/pylint: .build_history .build_history/isort .build_history/black $(FILES)
	@echo "Linting with pylint"
	$(VENV) ruff --fix
	$(VENV) pylint jiggle_version --fail-under 9.8
	@touch .build_history/pylint

# for when using -j (jobs, run in parallel)
.NOTPARALLEL: .build_history/isort .build_history/black

check: mypy test pylint bandit pre-commit

#.PHONY: publish_test
#publish_test:
#	rm -rf dist && poetry version minor && poetry build && twine upload -r testpypi dist/*

.PHONY: publish
publish: test
	rm -rf dist && hatch build

.PHONY: mypy
mypy:
	$(VENV) echo $$PYTHONPATH
	$(VENV) mypy jiggle_version --ignore-missing-imports --check-untyped-defs


check_docs:
	$(VENV) interrogate jiggle_version --verbose
	$(VENV) pydoctest --config .pydoctest.json | grep -v "__init__" | grep -v "__main__" | grep -v "Unable to parse"

make_docs:
	pdoc jiggle_version --html -o docs --force

check_md:
	$(VENV) linkcheckMarkdown README.md
	$(VENV) markdownlint README.md --config .markdownlintrc
	$(VENV) mdformat README.md docs/*.md


check_spelling:
	$(VENV) pylint jiggle_version --enable C0402 --rcfile=.pylintrc_spell
	$(VENV) codespell README.md --ignore-words=private_dictionary.txt
	$(VENV) codespell jiggle_version --ignore-words=private_dictionary.txt

check_changelog:
	# pipx install keepachangelog-manager
	$(VENV) changelogmanager validate

check_all_docs: check_docs check_md check_spelling check_changelog

check_own_ver:
	# Can it verify itself?
	$(VENV) ./dog_food.sh

#audit:
#	# $(VENV) python -m jiggle_version audit
#	$(VENV) tool_audit single jiggle_version --version=">=2.0.0"

install_plugins:
	echo "N/A"

.PHONY: issues
issues:
	echo "N/A"
