#!/usr/bin/env sh
set -eu

cat > /usr/share/nginx/html/config.js <<EOF
window.__ENV__ = {
  API_BASE: "${API_BASE:-/api}"
};
EOF
