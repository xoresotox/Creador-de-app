#!/usr/bin/env bash
# Sincroniza web/ → android/app/src/main/assets/web/ antes de compilar el APK.
# Uso:  bash scripts/sync-web.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/web"
DST="$ROOT/android/app/src/main/assets/web"

mkdir -p "$DST"
cp -fv "$SRC/index.html" \
       "$SRC/manifest.webmanifest" \
       "$SRC/sw.js" \
       "$SRC/icon-192.png" \
       "$SRC/icon-512.png" \
       "$DST/"
echo "Web assets sincronizados en: $DST"
