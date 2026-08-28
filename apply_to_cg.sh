#!/usr/bin/env bash
set -euo pipefail
CG=${1:-../cg}
ROOT=$(cd "$(dirname "$0")" && pwd)
if [ ! -d "$CG/cogym_kernel/worlds" ]; then
  echo "usage: $0 /path/to/prx0r/cg" >&2; exit 2
fi
mkdir -p "$CG/cogym_kernel/worlds/arena402"
cp -R "$ROOT/integration/cogym_kernel/worlds/arena402/"* "$CG/cogym_kernel/worlds/arena402/"
echo "Installed arena402.mechanism_lab into $CG/cogym_kernel/worlds/arena402"
echo "Install 402Arena in the same environment, then run: cd $CG && cg worlds"
