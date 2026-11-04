# JASMA — 10-Day Delivery Plan

A deliberate, day-by-day breakdown. Each day lists its goal, the concrete
deliverables, how we'll know it's done ("done when"), and any AWS cost impact.

The project is a learning exercise: a Python task-management REST API taken
from a bare FastAPI service to a container, to a cluster, to Terraform-managed
AWS infrastructure, to a CI/CD pipeline with observability. It intentionally
touches every layer a junior Cloud Engineer is expected to reason about.

---

## Day 1 — FastAPI foundation *(done)*

**Goal:** a local HTTP service that models the task domain cleanly, logs like a
production service would, and is covered by tests.

**Deliverables**
- `app/main.py` — FastAPI app with CRUD on `/tasks` and `/healthz` + `/readyz`
  probes.
- `app/models.py` — Pydantic v2 models (`Task`, `TaskCreate`, `TaskUpdate`) and
  a `Status` enum.
- `app/store.py` — in-memory `TaskStore` behind a narrow interface so it can
  be swapped for a DB later without changing the routes.
- `app/logging_config.py` — stdout JSON logger (one line per event) so logs
  slot straight into CloudWatch/Fluent Bit later.
- `tests/test_tasks.py` — `TestClient` tests for happy paths, 404s, and
  validation (422).

**Done when:** `pytest -q` is green and `curl localhost:8000/healthz` returns
`{"status":"ok"}`.

**Cost:** £0.

---

## Day 2 — Dockerise

**Goal:** the same app running inside a container, built from a small,
reproducible image.

**Deliverables**
- `Dockerfile` — multi-stage build on `python:3.12-slim`, non-root user,
  `uvicorn` as the entrypoint on port 8000.
- `.dockerignore` — keep `.venv`, caches, and tests out of the image.
- Image runs locally: `docker build -t jasma:dev . && docker run -p 8000:8000 jasma:dev`.

**Done when:** `/healthz` responds through the container, image is under
~200 MB, and it runs as a non-root UID.

**Cost:** £0.

---

## Day 3 — GitHub Actions CI

**Goal:** every push runs tests and builds the image.

**Deliverables**
- `.github/workflows/ci.yml` — jobs for `pytest` and `docker build` on pushes
  and PRs to `main`.
- Status badge in `README.md`.

**Done when:** a dummy PR shows a green check and a failing test blocks merge.

**Cost:** £0 (GitHub Actions free tier).

---

## Day 4 — Local Kubernetes (kind)

**Goal:** prove the container runs under Kubernetes before paying AWS.

**Deliverables**
- `k8s/` manifests: `Deployment`, `Service` (ClusterIP), liveness/readiness
  probes wired to `/healthz` and `/readyz`, resource requests + limits.
- `kind create cluster` + `kubectl apply -f k8s/` runbook in `docs/kind.md`.

**Done when:** `kubectl port-forward` to the service returns task data and
killing a pod triggers a restart that passes probes.

**Cost:** £0.

---

## Day 5 — Terraform hello-world

**Goal:** get comfortable with Terraform state and workflow against a trivial
AWS resource before the real infra.

**Deliverables**
- `infra/hello/` with a single S3 bucket (versioned, private) and remote state
  stored in that same bucket (or a sibling one) + DynamoDB lock table.
- `terraform init / plan / apply / destroy` runbook in `docs/terraform.md`.

**Done when:** apply and destroy both succeed cleanly and state is remote, not
local.

**Cost:** pennies. S3 + DynamoDB usage is negligible at this scale.

---

## Day 6–7 — AWS infrastructure via Terraform

**Goal:** the real stack — VPC, ECR, IAM, EKS — all codified.

**Deliverables**
- `infra/aws/` modularised:
  - `network/` — VPC, public + private subnets across 2 AZs, NAT (single, to
    keep cost down), route tables.
  - `ecr/` — one ECR repository for the `jasma` image, with lifecycle rule to
    keep only the last 10 images.
  - `iam/` — cluster role, node role, and an IRSA role the app pod will
    assume.
  - `eks/` — EKS cluster (one small managed node group, `t3.small` x2) with
    the OIDC provider enabled.
- AWS budget alert at **£10**, created before the first `apply`.

**Done when:** `kubectl get nodes` returns the node group and nothing is
hard-coded (all parameters flow through `variables.tf`).

**Cost:** **~£60/mo** for the EKS control plane (`$0.10/hr`) + node + NAT.
`terraform destroy` at the end of every session.

---

## Day 8 — Deploy to EKS

**Goal:** the Day 4 manifests, pointed at the real image in ECR, running on
EKS.

**Deliverables**
- Push the Day 2 image to ECR.
- Update `k8s/` to reference the ECR image URI.
- Add an `Ingress` (AWS Load Balancer Controller) or a `Service` of type
  `LoadBalancer`, whichever is cheaper to run briefly.
- `kubectl apply` succeeds, external DNS/IP serves `/healthz`.

**Done when:** `curl https://<lb>/healthz` from a laptop returns `ok`.

**Cost:** ALB is ~$16/mo if left on; destroy with the cluster.

---

## Day 9 — CI/CD with GitHub OIDC to AWS

**Goal:** no long-lived AWS keys — GitHub Actions assumes an AWS role via OIDC
to build, push to ECR, and roll out to EKS.

**Deliverables**
- Terraform: an IAM role trusting `token.actions.githubusercontent.com` with
  a trust policy scoped to this repo and `main` branch.
- `.github/workflows/cd.yml`: on push to `main`, build image → push to ECR →
  `kubectl set image` on the Deployment.
- Rollback runbook in `docs/cd.md`.

**Done when:** a commit to `main` ends with a new image running in the
cluster, with zero secrets stored in GitHub.

**Cost:** £0 beyond what Days 6–8 already cost.

---

## Day 10 — CloudWatch + AI summarisation endpoint

**Goal:** observability + one small AI feature that makes the project tell a
better story in interviews.

**Deliverables**
- Container Insights / Fluent Bit shipping pod logs to CloudWatch; a dashboard
  with request rate, error rate, latency, and pod CPU/memory.
- A new `POST /tasks/{id}/summarise` endpoint that calls a hosted LLM
  (Bedrock Claude, probably) to produce a one-sentence summary of the task's
  description. Model id + credentials via env + IRSA, not baked in.

**Done when:** logs are searchable in CloudWatch Logs Insights and the
summarise endpoint returns a plausible sentence end-to-end from the cluster.

**Cost:** CloudWatch Logs is a few pence/day at this volume; Bedrock usage is
pennies per call. Still `terraform destroy` at end of session.

---

## Working rules

- **Commit often, small commits.** Each day should be at least one commit,
  ideally several.
- **Destroy AWS between sessions** from Day 6 onwards. The $10 budget alert is
  a safety net, not a plan.
- **Keep the README roadmap checkboxes in sync** with reality — they're what
  future-me (and an interviewer skimming the repo) will read first.
- **Write it so you can talk to it.** If a decision is interesting (why single
  NAT, why IRSA over node role, why kind before EKS), note it in `docs/` as a
  short ADR.
