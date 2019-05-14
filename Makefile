.PHONY: docker docker-no-cache getdeps

getdeps:
	@mkdir -p build
	@echo "Download dependencies...  "
	@wget --show-progress -cq https://releases.hashicorp.com/terraform/0.11.13/terraform_0.11.13_linux_amd64.zip -O build/terraform.zip
	@wget --show-progress -cq	 https://github.com/adammck/terraform-inventory/releases/download/v0.8/terraform-inventory_v0.8_linux_amd64.zip -O build/terraform-inventory.zip
	@echo "OK"

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
