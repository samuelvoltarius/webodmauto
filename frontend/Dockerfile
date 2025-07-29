FROM node:18-alpine

# Arbeitsverzeichnis setzen
WORKDIR /app

# Package-Dateien kopieren
COPY package*.json ./

# Dependencies installieren
RUN npm ci --only=production

# Anwendungscode kopieren
COPY . .

# Anwendung bauen
RUN npm run build

# Nginx für statische Dateien
FROM nginx:alpine

# Nginx-Konfiguration kopieren
COPY nginx.conf /etc/nginx/nginx.conf

# Build-Artefakte kopieren
COPY --from=0 /app/dist /usr/share/nginx/html

# Port freigeben
EXPOSE 80

# Gesundheitscheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# Nginx starten
CMD ["nginx", "-g", "daemon off;"]