#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" != --apply ]]; then
  echo 'Offline plan: on a new Ubuntu 24.04 x86_64 host, install Docker Engine/Compose from the official apt repository and create /srv/resonant. Run with sudo bootstrap-host.sh --apply only on the approved VM.'
  exit 0
fi
[[ $EUID == 0 ]] || { echo 'Run using sudo on the approved VM' >&2; exit 1; }
[[ $(uname -m) == x86_64 ]] || { echo 'x86_64 Linux required' >&2; exit 1; }
source /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 24.04 ]] || { echo 'This bootstrap supports Ubuntu 24.04 only' >&2; exit 1; }
owner=${SUDO_USER:-ubuntu}
[[ "$owner" =~ ^[a-z_][a-z0-9_-]*$ && "$owner" != root ]] || { echo 'Use sudo from the owner SSH account' >&2; exit 1; }
apt-get update
apt-get install -y ca-certificates curl rsync python3
install -m 0755 -d /etc/apt/keyrings
curl --fail --silent --show-error --location https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
cat > /etc/apt/sources.list.d/docker.sources <<'EOF'
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: noble
Components: stable
Architectures: amd64
Signed-By: /etc/apt/keyrings/docker.asc
EOF
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
usermod -aG docker "$owner"
install -d -m 0755 -o "$owner" -g "$owner" /srv/resonant /srv/resonant/deploy /srv/resonant/releases /srv/resonant/runtime /srv/resonant/models
install -d -m 0700 -o 10001 -g 10001 /srv/resonant/state
echo 'Bootstrap complete. Reconnect SSH for Docker group membership. Docker-group membership is root-equivalent. SSH remains key-only per the VM image; firewall is managed by the exact-account provisioning script.'
docker version --format '{{.Server.Version}}'
docker compose version --short
