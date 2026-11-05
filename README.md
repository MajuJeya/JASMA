# JASMA — Cloud-Native Task Management Platform

[![CI](https://github.com/MajuJeya/JASMA/actions/workflows/ci.yml/badge.svg)](https://github.com/MajuJeya/JASMA/actions/workflows/ci.yml)

A learning project: a Python task-management REST API, built end-to-end on AWS
using Terraform, Docker, Kubernetes (EKS) and GitHub Actions.

## Status

**Day 3** — containerised and gated by GitHub Actions CI: `pytest` + `docker build`
run on every push and PR to `main`. Previous: multi-stage `python:3.12-slim`
Dockerfile, running as non-root `appuser` (UID 10001) on port 8000.

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then try it:

```bash
curl -s localhost:8000/healthz
curl -s -X POST localhost:8000/tasks -H 'content-type: application/json' \
  -d '{"title":"write terraform"}'
curl -s localhost:8000/tasks
```

API docs are auto-generated at `http://localhost:8000/docs`.

## Run in Docker

```bash
docker build -t jasma:dev .
docker run --rm -p 8000:8000 --name jasma jasma:dev
```

Then `curl localhost:8000/healthz` from another terminal.

## Roadmap

See [`docs/plan.md`](docs/plan.md) for the full per-day breakdown (goals,
deliverables, done-criteria, cost).

- [x] Day 1 — FastAPI + pytest
- [x] Day 2 — Dockerise
- [x] Day 3 — GitHub Actions CI
- [ ] Day 4 — Local Kubernetes (kind)
- [ ] Day 5 — Terraform hello-world
- [ ] Day 6–7 — AWS infra (VPC, ECR, IAM, EKS) via Terraform
- [ ] Day 8 — Deploy to EKS
- [ ] Day 9 — CI/CD with GitHub OIDC to AWS
- [ ] Day 10 — CloudWatch + AI summarisation endpoint

## Cost note

EKS control plane costs ~$73/month and is NOT in the AWS free tier. From Day 6
onwards, always `terraform destroy` when you stop work, and set an AWS budget
alert at $10 before the first `terraform apply`.
