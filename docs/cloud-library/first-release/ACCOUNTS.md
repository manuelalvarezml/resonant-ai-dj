# Accounts and credentials — sanitized audit

> D071 update: `manueldev` remains selected. The [serverless plan](serverless/README.md) uses a generated CloudFront HTTPS hostname; an owner domain/VM SSH access is unnecessary. Lambda quota increase and CDN Free-plan eligibility are the new account checks. Prior VM-specific instructions below are historical.

2026-10-02. Read-only audit requested by the owner. No secret values, token fragments, access-key IDs or full account IDs are recorded here. No resources or credentials were changed.

**Owner selection after the usage-limit interruption:** use `manueldev` /
`manuel-web`. Fresh STS succeeded again; the exact account and ARN are stored
privately in `output/cloud-preparation/aws-target.json` (mode 600). Account
selection is resolved. Do not request a new profile or use `default`.

## What is available

| Configuration | Observed result | Meaning |
|---|---|---|
| AWS `default` | STS succeeded; account ending **8455**, IAM user `manuel@instacash.pe`, region `us-east-1` | Appears work-associated; do not use for this deployment |
| AWS `manueldev` | STS succeeded; account ending **3649**, IAM user `manuel-web`, region `us-east-2` | Owner-selected deployment account; fresh STS reverified; spending still pending |
| AWS files | Both static-key profiles in `~/.aws/credentials`; regions in `~/.aws/config`; AWS CLI installed | Authentication works; Lightsail metadata reads also pass; mutation permissions/quota/capacity untested |
| Project OpenAI key | `AUTODJ_OPENAI_API_DEV_KEY` is present in the process and an assignment name exists in `~/.zshrc` | This is the variable `playlist.toml` selects; validity and billing ownership were not tested |
| Generic OpenAI key | `OPENAI_API_KEY` present in process and referenced in `~/.zshrc` | Not a fallback for the current PlaylistIQ configuration |
| Cloudflare/R2/Render/Railway/Vercel | No credential-variable names found in inspected process/startup files; no `wrangler` on PATH | No verified connection; other login mechanisms were not ruled out |
| Hetzner | No `HCLOUD_TOKEN` in inspected process/startup files; no standard `~/.config/hcloud/cli.toml`; no `hcloud` on PATH | New personal setup needed if selected |

`.bash_profile`, `.bashrc` and `.profile` are absent. `.zprofile` contains no matching provider credential names. `.zshrc` also references AWS tunnel variables; those are not AWS API credentials. Startup files were parsed as text, not executed. No keychain, unrelated credential stores or broad home scan was used.

AWS STS proves the principal/account in use at audit time. It cannot prove that the person owns the account, which payment card pays for it, or whether Lightsail permissions exist. Profile names are not proof of ownership.

## Inputs needed for deployment

1. **AWS target is selected:** `manueldev`, IAM `manuel-web`, account ending 3649, `us-east-2`. Exact-account checks use the private target file before each mutation; no further profile decision is needed.
2. **Budget:** accept a specific hosting envelope. Proposed fastest existing-account route is $44/month compute before tax, optional backups/domain and separately metered OpenAI use. A lower budget changes provider/sizing and requires a new cost check.
3. **Sharing:** choose shared password, email allowlist, or open link. Working plan uses a shared password pending the answer, with one immutable library for everyone.
4. **HTTPS address:** supply a personal domain/subdomain already owned, or decide the initial hostname approach. DNS authority has not been audited and no domain is assumed owned.
5. **OpenAI billing:** confirm that the configured project key is intended for this hosted release, or create a separate project key locally. Inject it server-side using the exact configured variable, with bounded usage. Existing validity is untested; no paid test call was made.

No passwords or secret strings need to be sent in this chat. Account identity, access preference, budget and domain name are sufficient planning answers; secrets stay in the local/private deployment environment.

## Mandatory AWS target guard for future execution

Use the owner-selected `--profile manueldev` explicitly. In the command subprocess clear inherited credential/session/profile overrides, then run `aws sts get-caller-identity --profile manueldev`. Compare the returned **full account ID internally** against the exact account selected by the owner and recorded in the private target file before any mutation; matching a four-digit suffix alone is insufficient. Do not print credentials or copy the identity response into a public artifact. Stop on mismatch, expiry or missing permission; never retry against `default`.

Deployment should use the narrowest practical rights after that identity check. Do not copy AWS credentials onto the application VM: this single-disk design does not need AWS API access at runtime. Secret validity and account permissions must be checked at execution time, since they can change.

## Read-only deployment metadata verified

`output/cloud-preparation/aws-readiness.json` records successful `get-bundles`,
`get-blueprints` and `get-regions --include-availability-zones` calls using only
the selected profile. Active candidates: `large_3_0` (8 GB, two vCPUs, 160 GB
disk, $44/month, 5,120 GB included transfer, one IPv4), `ubuntu_24_04`, and
`us-east-2a` (b/c also available). These reads do not prove create permission,
quota or actual instance capacity. No resources were created.

A dedicated RSA-4096 key pair is already prepared privately at
`output/cloud-config/ssh/resonant-lightsail-rsa` and its `.pub` file. Only the
public key will be imported during approved provisioning; the private key stays
local. RSA matches the [Lightsail import contract](https://docs.aws.amazon.com/lightsail/2016-11-28/api-reference/API_ImportKeyPair.html).
Before provision, supply the owner's current public IPv4 `/32` for SSH access. Verify
the SSH host fingerprint through the provider's trusted channel before upload;
the transfer script deliberately does not auto-accept an unknown host key.
