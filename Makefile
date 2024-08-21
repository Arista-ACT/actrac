lint:
	$${HOME}/.local/bin/poetry run ruff check actrac/ test/

format:
	$${HOME}/.local/bin/poetry run ruff check --fix actrac/ test/
	$${HOME}/.local/bin/poetry run black actrac/ test/

mypy:
	$${HOME}/.local/bin/poetry run mypy actrac/

unittest:
	$${HOME}/.local/bin/poetry run pytest --cov=actrac test/unit/

install-deps:
	curl -sSL https://install.python-poetry.org/ | python3 -
	$${HOME}/.local/bin/poetry config experimental.system-git-client true
	$${HOME}/.local/bin/poetry install

install-deps-prod:
	curl -sSL https://install.python-poetry.org/ | python3 -
	$${HOME}/.local/bin/poetry config experimental.system-git-client true
	$${HOME}/.local/bin/poetry install --without dev
