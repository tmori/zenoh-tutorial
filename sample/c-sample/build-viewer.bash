#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
tutorial_root="$(cd "${script_dir}/../.." && pwd)"
business_pack_root="${HAKONIWA_BUSINESS_PACK_ROOT:-${tutorial_root}/../hakoniwa-business-pack}"
foundation_prefix="${HAKO_FOUNDATION_INSTALL:-${business_pack_root}/work/foundation/install}"

cmake -S "${script_dir}" -B "${script_dir}/cmake-build-viewer" \
  -DZENOH_C_ROOT="${foundation_prefix}" \
  -DHAKO_ZENOH_TOPOLOGY_AGENT=ON \
  -DHAKO_ZENOH_TOPOLOGY_AGENT_ROOT="${foundation_prefix}"
cmake --build "${script_dir}/cmake-build-viewer"
