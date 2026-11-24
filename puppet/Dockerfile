# Puppet runner image: applies the manifest against the host's Docker daemon
FROM debian:bookworm-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends puppet-agent docker.io ca-certificates \
 || apt-get install -y --no-install-recommends puppet docker.io ca-certificates \
 ; rm -rf /var/lib/apt/lists/*
WORKDIR /project/puppet
ENTRYPOINT ["puppet", "apply"]
CMD ["manifests/site.pp"]
