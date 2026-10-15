# Image d'outillage word2robot (Podman) : Python, Robot Framework, Browser (Playwright + Chromium),
# Tesseract (OCR) et les serveurs MCP : Playwright MCP (+ son Chromium) et rf-mcp (Robot Framework).
# Le projet n'est pas copié dans l'image : il est monté dans /work par w2r.ps1 / w2r.
# Construction : .\w2r.ps1 build
#
# Versions figées : images de base par empreinte (sha256), Playwright MCP par version, paquets Python par
# requirements.lock (« w2r lock » pour le régénérer après un changement de requirements.txt).
FROM docker.io/library/node:22-bookworm-slim@sha256:c3de60bf2f9dd0ac6370e6117950ff62d6e339527e7472301c9c78a017978392 AS node

FROM docker.io/library/python:3.12-slim-bookworm@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258

# Node.js est requis par robotframework-browser (rfbrowser init) et Playwright MCP
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
 && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
 && apt-get update \
 && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-fra \
 && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Playwright MCP (relevé des localisateurs, étape 4) avec le Chromium de SA version de Playwright
ARG PLAYWRIGHT_MCP_VERSION=0.0.83
RUN npm install -g @playwright/mcp@${PLAYWRIGHT_MCP_VERSION} \
 && node /usr/local/lib/node_modules/@playwright/mcp/node_modules/playwright/cli.js install chromium

# requirements.lock s'il existe (versions exactes), sinon requirements.txt
COPY requirements.* /tmp/
# --with-deps : bibliothèques système et polices dont Chromium a besoin
RUN if [ -f /tmp/requirements.lock ]; then pip install -r /tmp/requirements.lock; \
    else pip install -r /tmp/requirements.txt; fi \
 && rfbrowser init --with-deps chromium

WORKDIR /work
CMD ["robot", "--version"]
