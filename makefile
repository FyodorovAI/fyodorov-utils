include .env

# Set up virtual environment
venv:
	python3 -m venv venv
	echo 'Run "source venv/bin/activate" to activate the virtual environment.'
	echo 'Run "make install" to install the requirements.'
	echo 'Run "make build" to build the package.'
	echo 'Run "make publish" to publish the package.'
	echo 'Run "make release" to build and publish the package.'

# Publish the package to GitHub Packages
publish:
	export API_TOKEN=${API_TOKEN} && echo 'token: ${API_TOKEN}' && python3 -m twine upload --username __token__ --password ${API_TOKEN} --verbose dist/*

# Install requirements from requirements.txt
install:
	uv pip install -r requirements.txt

# Install requirements from src/fyodorov_utils/requirements.txt
install-src:
	uv pip install .

build:
	rm -rf ./dist
	python3 -m build

release: install-src install build publish

lint:
	ruff check src/fyodorov_utils/

format:
	ruff format src/fyodorov_utils/