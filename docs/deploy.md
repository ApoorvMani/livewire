# Deploy

## Prerequisites

- VPS (DigitalOcean / Hetzner) running Ubuntu 22.04+
- Domain pointed to VPS IP via Cloudflare (DNS + proxy)
- Python 3.12+, Node.js 20+

## Steps

1. **Clone the repo on VPS**

   ```bash
   git clone https://github.com/yourorg/livewire.git /opt/livewire
   cd /opt/livewire
   ```

2. **Create virtualenv and install**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

3. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with:
   #   SECRET_KEY=<random-secret>
   #   DATABASE_URL=sqlite:////opt/livewire/livewire.db
   ```

4. **Seed the database**

   ```bash
   make seed
   ```

5. **Build the frontend**

   ```bash
   cd web
   npm install
   npm run build
   ```

6. **Set up reverse proxy (Caddy recommended)**

   ```caddyfile
   livewire.yourdomain.com {
       reverse_proxy localhost:8000
       root * /opt/livewire/web/dist
       try_files {path} /index.html
   }
   ```

7. **Set up systemd for the API**

   ```bash
   sudo cp ops/livewire-api.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now livewire-api
   ```

8. **Set up Cloudflare DNS + proxy**

   - Add an A record for `livewire` pointing to your VPS IP
   - Enable the proxy (orange cloud) for HTTPS

9. **Verify**

   ```bash
   curl -X POST https://livewire.yourdomain.com/api/auth/register \
     -H 'content-type: application/json' \
     -d '{"username":"test","password":"password123"}'
   ```

   Expected: `{"id":1,"username":"test","token":"..."}`

## Updating

```bash
cd /opt/livewire
git pull
source venv/bin/activate
pip install -e .
make seed
sudo systemctl restart livewire-api
cd web && npm install && npm run build
```
