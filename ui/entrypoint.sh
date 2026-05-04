#!/bin/sh
# 1. Créer le fichier env.js avec les variables d'environnement runtime
cat > /usr/share/nginx/html/env.js << EOF
window.__ENV__ = { API_URL: '${API_URL:-http://localhost:8000}' };
EOF

echo "Runtime config: API_URL=${API_URL:-http://localhost:8000}"

# 2. Injecter le <script> dans index.html si pas déjà présent
if ! grep -q "env.js" /usr/share/nginx/html/index.html; then
  sed -i 's|</head>|<script src="/env.js"></script></head>|' /usr/share/nginx/html/index.html
fi

exec "$@"
