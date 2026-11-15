#!/usr/bin/env bash
# Build the pinned, patched customer-gateway evaluation image.
#
#   ./build/build.sh                 # preferred: official pinned base + overlay copy
#   ./build/build.sh --from-source   # full source clone + patch + rebuild (slower)
#
# No customer secrets are used in this script. Both paths are hash-guarded before
# and after the product files are applied; a wrong base fails the build.
set -euo pipefail
cd "$(dirname "$0")"

IMAGE_TAG="${CUSTOMER_GATEWAY_IMAGE:-openhands-enterprise-customer-gateway-eval:1.92.0}"

# Pinned by digest, not the mutable ":1.92.0" tag — see docs/BASE-IMAGE-DIGESTS.txt.
# This is the linux/amd64 image manifest; re-verify before trusting it long-term, and
# override BASE_IMAGE explicitly for a different platform (e.g. arm64 dev machines).
DEFAULT_BASE_IMAGE="ghcr.io/openhands/enterprise-server@sha256:1fc805d90bbb97fc75583cda9b315bc9748713311c8b672eec6dfbdf9b19b974"
EXPECTED_SDK_VERSION="1.62.0"

if [ "${1:-}" = "--from-source" ]; then
  echo "== from-source build: fetch pinned base source, apply frozen patch, verify hashes =="
  OUT_DIR=".build/patched-src"
  rm -rf .build
  mkdir -p .build
  docker buildx build \
    -f Dockerfile.sourceprep \
    --target patched-source \
    -o "type=local,dest=${OUT_DIR}" \
    .
  echo "== build the Enterprise app image from the patched source =="
  docker build \
    -f "${OUT_DIR}/containers/app/Dockerfile" \
    -t "${IMAGE_TAG}" \
    --build-arg OPENHANDS_BUILD_VERSION=1.92.0-customer-gateway-eval \
    "${OUT_DIR}"
else
  echo "== preferred build: official pinned base image + reviewed overlay copy =="
  # Network access only: pull the public, anonymous ghcr.io/openhands/enterprise-server
  # image. No credentials are required or used. Defaults to a digest pin, not the
  # mutable ":1.92.0" tag; override BASE_IMAGE explicitly if you need a different
  # platform's digest from docs/BASE-IMAGE-DIGESTS.txt.
  docker build \
    -f Dockerfile.customer-gateway \
    -t "${IMAGE_TAG}" \
    --build-arg "BASE_IMAGE=${BASE_IMAGE:-$DEFAULT_BASE_IMAGE}" \
    .
fi

echo "== verifying the ACTUALLY INSTALLED openhands-sdk package version in the built image =="
# pyproject.toml pinning "openhands-sdk==1.62.0" is a source-tree claim; this checks
# what uv/pip actually resolved and installed into the image that will run.
ACTUAL_SDK_VERSION="$(docker run --rm --entrypoint python "${IMAGE_TAG}" \
  -c "import importlib.metadata as m; print(m.version('openhands-sdk'))")"
if [ "${ACTUAL_SDK_VERSION}" != "${EXPECTED_SDK_VERSION}" ]; then
  echo "SDK VERSION MISMATCH: expected ${EXPECTED_SDK_VERSION}, image has ${ACTUAL_SDK_VERSION}." >&2
  echo "Refusing to hand off an image whose installed SDK doesn't match what was verified." >&2
  exit 1
fi
echo "openhands-sdk ${ACTUAL_SDK_VERSION} confirmed installed in ${IMAGE_TAG}."

echo "Built ${IMAGE_TAG}"
echo "Set APP_IMAGE=${IMAGE_TAG} in your .env before 'docker compose up -d'."
