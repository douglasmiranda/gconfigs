.PHONY: clean clean-test clean-pyc clean-build help
.DEFAULT_GOAL := help

help: ## show make targets
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf " \033[36m%-20s\033[0m  %s\n", $$1, $$2}' $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache/

format: ## format code using black (https://github.com/ambv/black)
	poetry run black gconfigs/ tests/

lint: ## use black to show diff of formatted code
	poetry run black --diff gconfigs/ tests/

test: ## run tests quickly with the default Python
	poetry run pytest gconfigs tests/ -s

coverage: ## run tests quickly with the default Python
	poetry run coverage run --source gconfigs -m pytest tests/
	poetry run coverage report -m

full_test: ## check style, run tests and show coverage reports
	@printf "\033[34m$1Step 1 - Cheking Code Style With Black. (If there's something that could look better you will see the diff)\033[0m\n"
	@$(MAKE) lint
	@printf "\033[34m$1Step 2 - Running Tests. (Wait for coverage report)\033[0m\n"
	@$(MAKE) coverage
	@printf "\033[34m$1Step 3 - Cleaning Coverage Files\033[0m\n"
	@$(MAKE) clean-test

release: clean ## package and upload a release
	poetry run python setup.py sdist upload
	poetry run python setup.py bdist_wheel upload

dist: clean ## builds source and wheel package
	poetry run python setup.py sdist
	poetry run python setup.py bdist_wheel
	ls -l dist

readme: ## make readme with rst2html.py, output: ./tmp/output.html
	poetry run python setup.py --long-description | poetry run rst2html.py - > ./tmp/output.html

install: clean ## install the package to the active Python's site-packages
	poetry run python setup.py install
