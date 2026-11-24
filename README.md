# Time Manager (Flask + SQLite) with Docker, Ansible & Puppet

A small task/time tracker: add tasks, start/pause a timer (one at a time), mark done,
see total time and top category.

## Structure
```
Dockerfile            app image (python:3.12-slim + gunicorn, non-root, healthcheck)
docker-compose.yml    plain run on :5050
app/                  Flask app + UI
ansible/              Dockerfile (Ansible runner), inventory.ini, deploy.yml
puppet/               Dockerfile (Puppet runner), manifests/site.pp
Makefile              shortcuts
```

## Run (Docker Desktop must be running)
```
make run       # Compose      -> http://localhost:5050
make ansible   # Ansible       -> http://localhost:5051
make puppet    # Puppet        -> http://localhost:5052
make down
```
Ansible and Puppet run inside their own containers (built from their Dockerfiles)
and control your Docker daemon through the mounted /var/run/docker.sock, so nothing
needs to be installed on the Mac.

## How it works
- **Dockerfile**: builds the app image.
- **Ansible** (`deploy.yml`): builds the image, creates a volume, runs the container, checks /health.
- **Puppet** (`site.pp`): declares the image, volume and running container as idempotent `exec` resources.
  Run it twice: the second run changes nothing.

## Optional: run tools directly on the host
```
brew install ansible && ansible-galaxy collection install community.docker && pip3 install docker
cd ansible && PROJECT_DIR=$(cd ..; pwd) ansible-playbook -i inventory.ini deploy.yml
FACTER_project_dir=$PWD puppet apply puppet/manifests/site.pp   # needs puppet installed
```
