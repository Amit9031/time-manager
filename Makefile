SOCK=-v /var/run/docker.sock:/var/run/docker.sock
PROJ=-v $(PWD):/project -e PROJECT_DIR=$(PWD)

run:            ## plain docker compose  -> :5050
	docker compose up -d --build

ansible:        ## deploy via Ansible container -> :5051
	docker build -t tm-ansible ansible
	docker run --rm $(SOCK) $(PROJ) tm-ansible deploy.yml

puppet:         ## deploy via Puppet container -> :5052
	docker build -t tm-puppet puppet
	docker run --rm $(SOCK) $(PROJ) -e FACTER_project_dir=$(PWD) tm-puppet manifests/site.pp

down:
	-docker compose down
	-docker rm -f timemanager-ansible timemanager-puppet
