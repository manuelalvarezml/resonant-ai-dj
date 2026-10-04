# First shared-library release — deployment kit

> **Preserved VM kit:** D071 selects the [serverless plan](../../docs/cloud-library/first-release/serverless/README.md). These commands provision a VM and do not deploy that architecture. No VM was provisioned.

This kit is prepared locally. No host has been purchased, no music uploaded and
no service deployed by this task. The selected AWS identity is profile
`manueldev`, IAM user `manuel-web`, account ending `3649`, region `us-east-2`.
The old `default` profile is prohibited. See the maintained
[preparation status](../../docs/cloud-library/first-release/README.md).

The app serves one frozen library, one existing DJ mix and PlaylistIQ. Audio
analysis remains local. Guests use a shared access password and see the same
library; their saved playlists/favorites stay in their own browser. Caddy
protects the entire site, terminates TLS, compresses JSON/text, and is the only
public service. Node serves verified files and a bounded, single-job Python
planner. No PostgreSQL, S3, CDN, hosted analyzer or multi-user database is needed
for this release.

## Prepared artifacts and remaining gates

Run commands from the repository root unless a step explicitly says **on host**.

| Local artifact | Purpose |
| --- | --- |
| `output/cloud-releases/first-release` | 187 complete MP3s, sanitized public catalog/UI, one mix and private frozen planner/features |
| `output/cloud-models/first-release` | Six pinned MuQ text assets; no copied Python environment or audio analyzer weights |
| `output/cloud-runtime/first-release` | Allowlisted Linux Docker build context; immutable `runtime-source.json` records its identity |
| `output/cloud-config/first-release` | Private mode-600 configuration; hostname/OpenAI key may remain blank until supplied |
| `output/cloud-config/ssh/resonant-lightsail-rsa` | Prepared private RSA key; only its `.pub` file is imported into Lightsail |
| `output/cloud-preparation` | Local HTTP, planner parity, model-copy, AWS identity/offer and dependency metadata evidence |

The release ID is
`4a4bb92196ed75cc95ac19ec6a25bd5062ed31cdabb0eb30ebca0f83d5b5ff57`.
The release contains 415 inventoried files / 2,075,449,410 bytes, including
1,910,985,140 MP3 bytes. The model bundle is 2,663,058,281 bytes including its
manifest. Uploading both therefore needs about 4.74 GB before the small runtime
context and container packages. Private artifacts and secrets remain outside Git.

Before spending or uploading, settle the **$44/month instance allowance**, public
hostname/DNS, owner IPv4 `/32`, and server-side OpenAI key. The selected Lightsail
offer was verified read-only: `large_3_0`, 8 GB / 2 vCPU / 160 GB, public IPv4,
`ubuntu_24_04`, `us-east-2a`. Price excludes tax, OpenAI requests, optional
snapshots and usage overages. Offer metadata does not prove create permission,
quota or available capacity. [AWS pricing](https://aws.amazon.com/lightsail/pricing/)
and [SSH key import requirements](https://docs.aws.amazon.com/lightsail/2016-11-28/api-reference/API_ImportKeyPair.html).

Linux dependency metadata is checked for all 61 pinned packages. **The Linux
image has not been built or executed on this Mac**; the Docker daemon was
unavailable and was not started under current memory pressure. Target Linux
installation/imports, one bounded uncached text inference, HTTPS and live
OpenAI/browser checks are mandatory gates below, not completed evidence.

## 1. Local verification and reproducible source packaging

```sh
python3 -m unittest discover -s deploy/first-release -p 'test_*.py' -v
python3 deploy/first-release/verify-release.py output/cloud-releases/first-release
python3 deploy/first-release/verify-models.py output/cloud-models/first-release
python3 deploy/first-release/verify-runtime.py output/cloud-runtime/first-release
```

The prepared runtime context can be reproduced into a **new** directory:

```sh
python3 deploy/first-release/package-runtime.py --output output/cloud-runtime/next
```

This copies only named deployment files and runtime `.py`/`.json` sources. It
never packages Git, dotenv files, virtual environments, user music or model
weights. Source hashes and exact inventory are checked before build and again
after transfer. Changes to planner source may require re-exporting its frozen
snapshot and regenerating the release; the parity verifier detects a mismatch.
Never overwrite a published release directory or edit its `release.json`.

Optional metadata refresh (small official upstream metadata; no wheel/model
download or install):

```sh
packages/prompt-to-playlist/.venv/bin/python deploy/first-release/check-linux-metadata.py --output output/cloud-preparation/linux-dependency-metadata.json
```

## 2. Exact-account provisioning plan

Use the full account from the private identity evidence; do not paste keys or use
the work-associated default profile. Replace `ADMIN_CIDR` below with the owner's
current public IPv4 plus `/32`. This command is **offline by default**:

```sh
target_account=$(python3 -c 'import json; print(json.load(open("output/cloud-preparation/aws-target.json"))["account_id"])')
python3 deploy/first-release/provision-lightsail.py \
  --profile manueldev --account-id "$target_account" \
  --region us-east-2 --zone us-east-2a \
  --instance resonant-first-release --bundle large_3_0 --blueprint ubuntu_24_04 \
  --keypair resonant-first-release \
  --public-key-file output/cloud-config/ssh/resonant-lightsail-rsa.pub \
  --admin-cidr ADMIN_CIDR --accepted-monthly-usd 44
```

Only after the spending decision, repeat with `--apply`. It clears inherited
`AWS_*` overrides, checks STS account equality, checks bundle price/RAM/disk/IPv4
and the exact supported OS **before mutations**, optionally imports the scoped
RSA public key, creates one instance, restricts SSH to `/32` and attaches a static
IPv4. It refuses unrelated existing resources and does not overwrite key pairs.
No private SSH key is uploaded. The prepared key is RSA 4096 because Lightsail
imports require `ssh-rsa`; an Ed25519 public key is rejected locally.

If AWS returns an ambiguous create failure, inspect the same named resources;
do not change names and create duplicates. There is no automatic deletion.

## 3. Bootstrap the approved host and transfer immutable files

Verify the new SSH host key against trusted AWS console/session evidence before
adding it to `known_hosts`; scripts never accept unknown host keys automatically.
Use `ubuntu@PUBLIC_IP` and the prepared private key for SSH. Copy only
`bootstrap-host.sh` first, then **on host**:

```sh
sudo bash bootstrap-host.sh --apply
```

Bootstrap requires Ubuntu 24.04 and `x86_64`, installs Docker from its official
repository, creates `/srv/resonant`, and gives the owner Docker access. Reconnect
SSH afterward for group membership. Docker group membership is root-equivalent.
The state directory belongs to service UID 10001 with mode 700. Docker Compose
must support `env_file: format: raw` (Compose 2.30 or later).

Local upload plan; add `--apply` only after the target host is approved and its
host key verified:

```sh
python3 deploy/first-release/upload.py --host PUBLIC_IP --user ubuntu \
  --identity output/cloud-config/ssh/resonant-lightsail-rsa \
  --release output/cloud-releases/first-release \
  --models output/cloud-models/first-release \
  --runtime output/cloud-runtime/first-release
```

Transfer resumes partial files and uses explicit manifests/allowlists. Release
and context directories are named by their digests. A different existing model
manifest is refused. Full remote checks run before success. No secrets or
listener plaintext password are transferred by `upload.py`.

## 4. Build and validate on Linux before starting the site

**On host**, set the exact release path and runtime source digest from the upload
plan. Use a digest-derived immutable image tag, not `latest`:

```sh
cd /srv/resonant/deploy
release_id=4a4bb92196ed75cc95ac19ec6a25bd5062ed31cdabb0eb30ebca0f83d5b5ff57
runtime_digest=87e7d95c43165a7cf00d9938e145e38a1d6b857468b4edc9e274ec993af5ff9e
image_tag="resonant:${runtime_digest:0:16}"
bash build-runtime.sh "/srv/resonant/runtime/$runtime_digest" "$image_tag"
python3 linux-acceptance.py --image "$image_tag" \
  --release "/srv/resonant/releases/$release_id" --models /srv/resonant/models \
  --state /srv/resonant/state --output evidence/linux-first-release.json
```

Build uses pinned Python/Node images, CPU-only PyTorch and a fully pinned runtime
closure. `pip check` and imports must pass. MuQ 0.1.0 is the only source release;
its small pure-Python package uses the pinned setuptools backend.

Linux acceptance runs with networking disabled, 7 GB memory, 2 CPUs, PID limit,
read-only filesystem and no capabilities. It checks exact file hashes, imports,
one fresh generic text vector, identical cache replay and all **60 planner parity
cases across all five profiles**. No audio is analyzed and no OpenAI request is
made. The text worker has its own time/RAM bounds. Failed/OOM/timeout results do
not authorize activation: inspect evidence, adjust the concrete configuration,
and rerun into a new evidence filename.

## 5. Private configuration, DNS, activation and public acceptance

Private files were generated locally without displaying their contents. If a
new set is needed, this command refuses to overwrite any existing directory:

```sh
python3 deploy/first-release/prepare-config.py --output output/cloud-config/new-release
```

Set `.env` hostname/image/release path; set only
`AUTODJ_OPENAI_API_DEV_KEY` in `app.env` to the project OpenAI key. Leave the
generated distinct proxy/session secrets and Caddy bcrypt hash intact. Never
paste secrets into commands, chat, Git or container build arguments. Keep all
three files mode 600. Copy **only** `.env`, `app.env`, `caddy.env` to
`/srv/resonant/deploy` using the verified SSH connection. Keep
`listener-password.txt` local. Do not run `docker compose config` without
`--quiet`, because resolved output can include secrets.

Point the chosen hostname's A record at the static IPv4; avoid a stale AAAA
record. TCP 80/443 must reach Caddy for automatic certificates. App port 4175 is
not published. Once DNS resolves correctly, **on host**:

```sh
python3 activate.py --release "/srv/resonant/releases/$release_id" \
  --image "$image_tag" --linux-evidence evidence/linux-first-release.json
python3 activate.py --release "/srv/resonant/releases/$release_id" \
  --image "$image_tag" --linux-evidence evidence/linux-first-release.json --apply
```

The first command checks configuration/evidence without starting services. The
second checks the exact tested image ID and model manifest, starts Compose,
waits for health, records previous configuration and switches the current
release pointer. If startup fails it attempts the previous configuration and
keeps the previous pointer. Inspect status if recovery is incomplete.

Before starting serving containers, activation also runs `caddy validate` in the
exact pinned Caddy Linux image without publishing ports; failed validation stops
activation and keeps expanded configuration out of terminal output. Local Caddy
validation remains unrun: a temporary Mac binary download could not be verified
against the release checksum, so it was not executed. This is a limitation of
that local check, not evidence about the upstream release.

From the **local Mac**, validate the actual public origin with the retained
listener password file:

```sh
python3 deploy/first-release/verify-https.py --origin https://PUBLIC_HOSTNAME \
  --password-file output/cloud-config/first-release/listener-password.txt \
  --release-id 4a4bb92196ed75cc95ac19ec6a25bd5062ed31cdabb0eb30ebca0f83d5b5ff57 \
  --output output/cloud-preparation/https-first-release.json
```

This verifies the real certificate chain, password denial for every class of
content, secure session cookie, exact release/catalog, three MP3 byte-range
paths, mix ranges, CSRF rejection and owner/private route denial. It never sends
credentials to a redirect or calls PlaylistIQ. Then perform one real PlaylistIQ
request with the configured API key and verify playback/seeking and saved
playlists on desktop and mobile before sharing. The launch check is not complete
until these last results are recorded in the main release checklist.

## Operations and rollback

The initial prompt quota is 30 requests/day for the shared site, one active job
at a time. Quota survives restarts; it is not an exact dollar cap. Set spending
controls on the OpenAI project separately. Python jobs are bounded and their
process groups are reaped; interrupted prompts can be retried. Private request
audits retain at most 200 request pairs / seven days. Docker logs rotate at
three 5 MB files per service. Audio/models are immutable mounts.

To roll back, retain the previous immutable release, exact image and its Linux
acceptance evidence, then run `rollback.sh` with the same arguments as activation
and `--apply`. It uses the same guards; it does not delete a newer release. Run
the HTTPS check against the restored release ID. A previous `.env` backup alone
is not evidence that a release was tested. Keep secret files, source music and
immutable release/model bundles backed up independently of the VM. VM snapshots
are an optional additional paid decision.

To stop the app temporarily, use `docker compose stop` in the deployment
directory. Stopping the VM does **not** cancel Lightsail instance billing.
Instance/static-IP deletion is a separate explicit action after preserving any
needed state; this kit intentionally contains no automatic destructive teardown.
