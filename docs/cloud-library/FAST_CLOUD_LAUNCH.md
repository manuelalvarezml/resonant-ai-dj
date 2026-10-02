# Fast cloud launch with stable connections

## 2026-10-02 — First launch simplified to one owner/shared catalog

The owner now requests one shared read-only music library for link visitors, keeping analysis local. A parallel local web preview is implemented at port 4174; current qualified catalog has 187 MP3s. Local preview and code push are authorized; actual cloud publication follows preview review. Multi-tenant accounts and visitor uploads are deferred. [Current implementation and simplified launch plan](../../packages/web-player/docs/WEB_EDITION.md) supersede the earlier first-release scope below.

2026-09-12 · planning revision 1.3 · D057 / CD018. **Plan ready; no cloud
implementation, accounts, uploads, spending or deployment authorized.**
This is the current launch recommendation following the user's preference for
less manual work and fewer migrations. Start here before the older B2 packet.

D058 adds the product north star that this infrastructure must eventually
support: editable manual/PlaylistIQ-assisted playlists, continuous in-app
playback across owned and officially supported sources, and an occasional
rights-aware playlist-file download from the playlist ellipsis menu. The first
private release may support owned R2 tracks only; provider adapters must declare
play and download capabilities separately. A playlist archive is not a mix.

## Recommended route

Use **Cloudflare Workers Static Assets + one Worker API + private R2 + D1 +
Cloudflare Access**, connected to the existing repository. Keep the current
player and its `/api/v1` adapter. Use one app origin and separate persistent
preview/production resources. The initial audience remains one owner, then
three invited people, then at most ten. This recommendation is for that private
product; it is not a promise that the same auth/database will suit every future
public business.

R2 replaces B2 as the preferred planning default because it removes a provider
account, external storage credentials/region setup and the likely later B2→R2
move. B2 remains the lowest-cash alternative. The old cost workbook and B2
experiment are retained as history, not silently relabeled as R2 evidence.
The user accepted more setup effort; no budget increase is inferred.

Workers supports static assets and API code in one deployment. Resource bindings
connect the Worker directly to D1/R2; this avoids manually distributing service
keys between those components. Git integration supports deployment on pushes
and preview versions. These are documented capabilities, not a measured launch
of this application. [S059: assets](https://developers.cloudflare.com/workers/static-assets/),
[S060: bindings](https://developers.cloudflare.com/workers/runtime-apis/bindings/),
[S061: Git integration](https://developers.cloudflare.com/workers/ci-cd/builds/git-integration/github-integration/).

## Fastest useful release, by stage

| Stage | Concrete work after authorization | Exit / checkpoint |
|---|---|---|
| 0 — Settle once | Owner accepts private audience, R2 recommendation, budget/region policy, account/domain choice and generated-only trial envelope | One recorded decision; no source audio implied |
| 1 — Foundation | Create separate preview/prod Worker, R2 and D1 resources; Access allowlist; repository integration; infrastructure manifest and scoped deployment secret | One reproducible preview deployment; unauthenticated requests denied on every route |
| 2 — Connect listening | Implement catalog pagination and playback capabilities from the existing API contract; tenant membership checks; persistent editable favorites/playlists with revisions; continuous playlist queue; frontend account bootstrap/sign-out | Real private catalog, play/pause/seek/renewal, ordered playlist listening, cross-device collection state and explicit source-unavailable UI |
| 3 — Automate ingestion | One owner import command handles selected files, hash/probe manifest, resumable upload, verification, publish, retries and cleanup; no hand-entered SQL or per-track URLs | Generated fixtures publish only after verification; retry does not duplicate objects or rows |
| 4 — Prove and promote | Isolation, range/expiry/revocation, quota/race checks, restore/export/delete, rights-aware playlist archive with omissions/manifest and actual-device playback; publish the same tested build to the persistent production app | Evidence attached; owner-only use begins only within approved scope |
| 5 — Invite and extend | Validate the 3-user quota/isolation path before ten; add browser uploads/background compute only when their bounded verification/operating costs are accepted | Existing app origin, identities, data IDs and storage stay in place |

The existing frontend is complete. The backend, account synchronization, cloud
import command, cloud upload UI and infrastructure automation above **must still
be built**. A static deploy alone would still be a browser-local player.
This plan reduces the critical path to private listening; analysis, automatic
mixing, public signup and payments are separate features. There is no measured
completion-time estimate or guarantee of a one-click first setup.

## Connections to establish once

| Connection | Initial setup | Routine updates |
|---|---|---|
| Repository → deployment | Restricted app/repository authorization; package root/watch paths; build/check/migration script; protected production branch | Push reviewed code; checks and deployment run automatically |
| Worker → `ASSETS`, `DB`, `MEDIA` | Stable binding names in versioned Wrangler configuration; persistent resource IDs per environment | Reuse bindings; app releases do not recreate buckets or databases |
| Browser → app/API | One origin, `/api/v1`, Access login and same-origin session | No API URL edits for ordinary releases; config is generated per environment |
| Access → application identity | Validate signature, issuer, audience and expiry; server membership table keyed by an internal user ID and external issuer/subject | Invite/revoke users; email is a mutable attribute, not the tenant key |
| Owner importer → private storage/API | Scoped bucket credentials and service identity outside source control; tenant authorization fixed server-side | One explicit folder/batch command; credentials retained in a local secret store, rotated when needed |
| Budget/cleanup/backup → resources | Quotas, usage counters, alerts, expired-upload cleanup and tested export/restore wired at setup | Automatic bounded jobs plus actionable failure notices; no routine dashboard cleanup |

Access JWT validation and membership checks belong on the server; a client-sent
user/tenant ID is not authority. Protect static assets, API, workers.dev,
custom-domain and preview routes; test alternate URLs rather than assuming one
policy covers everything. Never connect pull-request previews to production
music or secrets. [S063: JWT validation](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json/),
[S053: Worker Access](https://developers.cloudflare.com/workers/configuration/cloudflare-access/).

## Small up-front choices that prevent avoidable migrations

- Keep API DTOs separate from D1 rows and object keys. The player receives public
  track/source IDs and short-lived playback URLs, never storage credentials.
  Current [consumer API](../../packages/web-player/docs/API.md) remains the entry contract.
- Give users, tenants, tracks and source versions immutable internal IDs now.
  Store original hashes, source versions and descriptor provenance. Never make
  an email address, filename, signed URL or provider bucket name a permanent ID.
- Persist playlists/favorites in the server database with tenant keys and a
  revision for conflict detection. The current HTTP adapter deliberately keeps
  preferences in memory; account sync is new implementation, not already done.
- Keep original media private under unique publication keys; never issue upload
  URLs for published keys. Keep staging separate. A staging upload can be retried
  or replaced, so HEAD/ETag/client claims alone do not prove audio hash/decodability.
- First private ingestion uses a **trusted owner CLI**, preserving D055's local
  verification boundary but automating its steps. Record this authority honestly.
  Publish only the exact verified bytes; bind object identity, size, digest and
  source version. For untrusted browser uploads, add independent background
  verification before publication; do not expose an unrestricted “mark verified” API.
- Keep audio/large versioned descriptor artifacts in R2; keep memberships,
  catalog metadata, job state and compact descriptors in D1. Add an outbox/job
  schema and idempotency keys now, without paying for an unused queue/compute
  fleet. A later analysis service consumes these versioned jobs and writes results;
  it does not replace the player or change who owns the catalog.
- Version infrastructure and forward-compatible SQL migrations in the repo.
  CI runs checks, backs up before schema changes, applies additive migrations
  and deploys one immutable build. Destructive changes need a later deliberate
  migration. Roll back code only when the current schema is compatible; never
  assume a Worker rollback also rolls back a database.

Minimum backend tables: users, external identities, tenants/memberships,
tracks/source versions, playlists/items, favorites, upload intents, jobs/outbox,
usage reservations and audit events. Add indexes for tenant and cursor queries.
Minimal operator commands should be `setup`, `doctor`, `import`, `deploy`,
`backup`, `restore-test`, `cleanup`—proposed command responsibilities, not
executables delivered in this revision. Setup must be idempotent and print
resource IDs/instructions, never secrets.

## Cost and scale boundaries

The unchanged [economics revision 2.0](UNIT_ECONOMICS.md) models R2 plus free
control-plane tiers at approximately **$0 / $0.23 / $1.08 monthly** for 1/3/10
people, with the modeled storage/operation allowances. These are estimates,
not measured bills or guaranteed ceilings. The proposed per-person ceiling
remains **8 GB AND 500 tracks**, subject to Q017's owner answer. Taxes, domain,
paid compute, backups beyond the model and founder time are additional.

Current R2 Standard pricing includes 10 GB-month free, then $0.015/GB-month,
with separate operation allowances and no egress bandwidth fee. Use Standard
for active tracks. [S001: R2 pricing](https://developers.cloudflare.com/r2/pricing/).
Workers Paid starts with a $5 subscription; it can exceed the existing $5 total
cap once storage is added. If Free CPU/request limits fail, stop and revise the
budget or scope—do not auto-upgrade. Hashing/decoding/ML does not belong in the
10 ms Free request budget. [S046: Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/),
[S058: limits](https://developers.cloudflare.com/workers/platform/limits/).

D1 Free has a 500 MB per-database ceiling, distinct from its aggregate storage
allowance; Paid increases a database to 10 GB. Use indexed, paginated metadata
queries and measure headroom. D1's row-read/write quotas also matter.
[S062: D1 limits](https://developers.cloudflare.com/d1/platform/limits/),
[S047: D1 pricing](https://developers.cloudflare.com/d1/platform/pricing/).
Access's free plan is aimed at teams under 50 users, fitting the proposed
private trial; verify account eligibility/terms at setup.
[S064: Access](https://www.cloudflare.com/sase/products/access/).

R2 alerts and application quotas are not a provider-enforced dollar hard cap.
Count reservations, unfinished uploads, retries, copies and backup bytes; limit
concurrency and capability issuance; stop admissions below the approved envelope.
Prove this before real uploads. The first proposed test can retain D055's
1 GB / 6 GB ingress / 10 GB egress / 8 active hours / 7 days / $1 envelope inside
$5/month, but **its R2 resource, signing, verification and cleanup protocol must
be revised and reviewed first**. Neither the B2 nor an R2 trial is approved here.

## When to choose more infrastructure at the beginning

If the next release is actually intended for public self-service accounts,
subscriptions, or substantial relational/vector workloads, choose consumer
auth and PostgreSQL before the first live account/data import. A concrete
alternative is Supabase Auth/Postgres plus the same Cloudflare app and R2.
This adds a provider connection now and avoids an Access→consumer-auth and
D1→Postgres migration later. Supabase's Pro baseline is currently $25/month,
so this cannot be assumed compatible with the $5 cap; Free is not a promise
that production growth stays free. [S010: Supabase pricing](https://supabase.com/pricing).

For the currently documented private ten-person scope, that extra provider is
not justified yet. This is an engineering judgment based on audience and
budget, not proof of infinite D1/Access scalability. Future AI/analysis services
will need their own new connection once; stable job/API contracts keep ordinary
feature releases from requiring every existing connection to be redone.
No honest plan can eliminate all future migrations or account decisions.

## Resume here

Plan complete. Next dependent step is owner acceptance of the provider/budget
and a bounded execution scope, then a **revised R2 owner packet**, not execution
of the stale B2 recipe. Preserve G001–G010, unrun EX001–EX007, D055 history and
economics 2.0. Log future runs in registers/events with actual invoices, device
results, cleanup evidence and source identities. The local design completion
is separately recorded in the [player checkpoint](../../packages/web-player/docs/REDESIGN_PLAN.md).
