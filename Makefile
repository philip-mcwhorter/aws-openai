SHELL := /bin/bash

init: $(.env)
	python3.11 -m venv .venv
	. .venv/bin/activate
	pip install -r requirements.txt
	echo -e "OPENAI_API_ORGANIZATION=PLEASE-ADD-ME\nOPENAI_API_KEY=PLEASE-ADD-ME" >> .env

activate:
	. .venv/bin/activate

lint:
	terraform fmt -recursive
	pre-commit run --all-files
	black ./terraform/python/
