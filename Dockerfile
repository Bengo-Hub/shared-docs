# syntax=docker/dockerfile:1.7

# Stage 1 — build the MkDocs site from docs/ only (mkdocs.yml's default docs_dir).
# internal/, hospital-quotation/, library-service/, processa-integration/, tools/,
# and everything else at repo root is never read by `mkdocs build` and never
# lands in site/ — this build step doesn't change what's published either way.
FROM python:3.12-slim AS build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /docs

# git-revision-date-localized-plugin imports GitPython, which needs the `git`
# executable importable even though fallback_to_build_date handles the
# "no .git present" case gracefully — only the missing-binary case is fatal.
RUN apt-get update && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY docs/ ./docs/
COPY mkdocs.yml ./

RUN mkdocs build

# Stage 2 — minimal NGINX runtime.
FROM nginx:alpine

COPY --from=build /docs/site /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD wget -qO- http://localhost/healthz >/dev/null || exit 1
