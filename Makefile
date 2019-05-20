.PHONY: clean virtualenv test docker dist dist-upload

clean:
	find . -name '*.py[co]' -delete

virtualenv:
	virtualenv --prompt '|> tank <| ' env
	env/bin/pip install -r requirements-dev.txt
	env/bin/python setup.py develop
	@echo
	@echo "VirtualENV Setup Complete. Now run: source env/bin/activate"
	@echo

test:
	python -m pytest \
		-v \
		--cov=tank \
		--cov-report=term \
		--cov-report=html:coverage-report \
		tests/

docker: clean
	docker build -t tank:latest .

dist: clean
	rm -rf dist/*
	python setup.py sdist
	python setup.py bdist_wheel

dist-upload:
	twine upload dist/*

docker-dev: getdeps
	@echo "Build docker image...  "
	@docker build -f Dockerfile.dev -t mixbytes/tank:develop .
	@echo "OK"

push-dev: docker-dev
	@echo "Push docker image to registry...  "
	@docker push mixbytes/tank:develop
	@echo "OK"

docker:
	@echo "Build docker image w/o cache...  "
	@docker build --no-cache -t mixbytes/tank .
	@echo "OK"

push: docker
	@echo "Push docker image to registry...  "
	@docker push mixbytes/tank
	@echo "OK"
