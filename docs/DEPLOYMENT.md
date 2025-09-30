# Deployment Guide

This guide provides instructions for deploying the Greeting API to various environments.

## Table of Contents

- [Environment Setup](#environment-setup)
- [Production Checklist](#production-checklist)
- [Deployment Options](#deployment-options)
- [Docker Deployment](#docker-deployment)
- [Cloud Platforms](#cloud-platforms)
- [Monitoring](#monitoring)
- [Scaling](#scaling)

## Environment Setup

### Environment Variables

Create a `.env` file for your environment:

```env
# Server Configuration
PORT=3000
NODE_ENV=production

# Rate Limiting
RATE_LIMIT_WINDOW=15          # Window in minutes
RATE_LIMIT_MAX_REQUESTS=100   # Max requests per window
```

### Production Environment Variables

```env
PORT=3000
NODE_ENV=production
RATE_LIMIT_WINDOW=15
RATE_LIMIT_MAX_REQUESTS=1000  # Adjust based on your needs
```

## Production Checklist

Before deploying to production:

- [ ] Set `NODE_ENV=production`
- [ ] Configure appropriate rate limits
- [ ] Set up proper logging (Winston, Bunyan, etc.)
- [ ] Configure CORS for specific origins
- [ ] Set up monitoring and alerts
- [ ] Enable HTTPS
- [ ] Configure reverse proxy (nginx, Apache)
- [ ] Set up process manager (PM2, systemd)
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline
- [ ] Run security audit (`npm audit`)
- [ ] Update dependencies
- [ ] Configure health checks
- [ ] Set up log rotation

## Deployment Options

### Option 1: Traditional Server with PM2

#### Install PM2

```bash
npm install -g pm2
```

#### Create PM2 Ecosystem File

Create `ecosystem.config.js`:

```javascript
module.exports = {
  apps: [{
    name: 'greeting-api',
    script: './src/server.js',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true,
    max_memory_restart: '1G'
  }]
};
```

#### Deploy with PM2

```bash
# Start application
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Setup auto-restart on system boot
pm2 startup

# Monitor
pm2 monit

# View logs
pm2 logs greeting-api
```

### Option 2: Systemd Service

Create `/etc/systemd/system/greeting-api.service`:

```ini
[Unit]
Description=Greeting API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/greeting-api
Environment=NODE_ENV=production
Environment=PORT=3000
ExecStart=/usr/bin/node /var/www/greeting-api/src/server.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable greeting-api
sudo systemctl start greeting-api
sudo systemctl status greeting-api
```

## Docker Deployment

### Create Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM node:18-alpine

# Create app directory
WORKDIR /usr/src/app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start server
CMD [ "node", "src/server.js" ]
```

### Create .dockerignore

```
node_modules
npm-debug.log
coverage
.env
.git
tests
docs
*.md
.gitignore
```

### Build and Run

```bash
# Build image
docker build -t greeting-api:1.0.0 .

# Run container
docker run -d \
  --name greeting-api \
  -p 3000:3000 \
  -e NODE_ENV=production \
  -e RATE_LIMIT_WINDOW=15 \
  -e RATE_LIMIT_MAX_REQUESTS=1000 \
  --restart unless-stopped \
  greeting-api:1.0.0

# View logs
docker logs -f greeting-api
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - PORT=3000
      - RATE_LIMIT_WINDOW=15
      - RATE_LIMIT_MAX_REQUESTS=1000
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "node", "-e", "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
```

Run with Docker Compose:

```bash
docker-compose up -d
```

## Cloud Platforms

### Heroku

1. **Create Heroku app:**
   ```bash
   heroku create greeting-api
   ```

2. **Set environment variables:**
   ```bash
   heroku config:set NODE_ENV=production
   heroku config:set RATE_LIMIT_MAX_REQUESTS=1000
   ```

3. **Create Procfile:**
   ```
   web: node src/server.js
   ```

4. **Deploy:**
   ```bash
   git push heroku main
   ```

### AWS Elastic Beanstalk

1. **Install EB CLI:**
   ```bash
   pip install awsebcli
   ```

2. **Initialize:**
   ```bash
   eb init -p node.js greeting-api
   ```

3. **Create environment:**
   ```bash
   eb create greeting-api-env
   ```

4. **Set environment variables:**
   ```bash
   eb setenv NODE_ENV=production RATE_LIMIT_MAX_REQUESTS=1000
   ```

5. **Deploy:**
   ```bash
   eb deploy
   ```

### Google Cloud Platform (Cloud Run)

1. **Build and push to Container Registry:**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/greeting-api
   ```

2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy greeting-api \
     --image gcr.io/PROJECT_ID/greeting-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars NODE_ENV=production,RATE_LIMIT_MAX_REQUESTS=1000
   ```

### DigitalOcean App Platform

1. **Create `app.yaml`:**
   ```yaml
   name: greeting-api
   services:
   - name: web
     github:
       repo: your-username/greeting-api
       branch: main
     run_command: node src/server.js
     environment_slug: node-js
     envs:
     - key: NODE_ENV
       value: production
     - key: RATE_LIMIT_MAX_REQUESTS
       value: "1000"
   ```

2. **Deploy via CLI or UI**

## Nginx Reverse Proxy

Configure nginx as reverse proxy:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

For HTTPS with Let's Encrypt:

```bash
sudo certbot --nginx -d api.yourdomain.com
```

## Monitoring

### Application Monitoring

Add monitoring middleware (e.g., using Prometheus):

```javascript
const promClient = require('prom-client');
const register = new promClient.Registry();

// Metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});
```

### Health Checks

The API includes a health check endpoint at `/health`:

```bash
curl http://your-domain.com/health
```

Set up monitoring tools to check this endpoint regularly.

### Log Aggregation

Use logging services like:
- Loggly
- Papertrail
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Datadog
- New Relic

## Scaling

### Horizontal Scaling

The API is stateless and can be scaled horizontally:

1. **With PM2 (Cluster Mode):**
   ```javascript
   instances: 'max', // Use all CPU cores
   exec_mode: 'cluster'
   ```

2. **With Load Balancer:**
   - Deploy multiple instances
   - Use nginx, HAProxy, or cloud load balancer
   - Configure health checks

3. **With Kubernetes:**
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: greeting-api
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: greeting-api
     template:
       metadata:
         labels:
           app: greeting-api
       spec:
         containers:
         - name: greeting-api
           image: greeting-api:1.0.0
           ports:
           - containerPort: 3000
           env:
           - name: NODE_ENV
             value: "production"
   ```

### Performance Optimization

1. **Enable compression:**
   ```javascript
   const compression = require('compression');
   app.use(compression());
   ```

2. **Add caching:**
   ```javascript
   app.use((req, res, next) => {
     res.set('Cache-Control', 'public, max-age=300');
     next();
   });
   ```

3. **Use CDN for static assets**

## Security Considerations

1. **Environment Variables:** Never commit `.env` files
2. **HTTPS:** Always use HTTPS in production
3. **Rate Limiting:** Adjust based on expected traffic
4. **CORS:** Configure for specific origins
5. **Security Headers:** Helmet is already configured
6. **Updates:** Keep dependencies updated
7. **Secrets:** Use secret management services

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   lsof -ti:3000 | xargs kill -9
   ```

2. **Permission denied:**
   - Use port > 1024
   - Or run with sudo (not recommended)
   - Or use authbind

3. **Out of memory:**
   - Increase memory limits
   - Check for memory leaks
   - Optimize code

### Logs

Check logs for debugging:
```bash
# PM2
pm2 logs greeting-api

# Docker
docker logs greeting-api

# Systemd
journalctl -u greeting-api -f
```

## Rollback

If deployment fails:

```bash
# PM2
pm2 stop greeting-api
pm2 start old-version

# Docker
docker stop greeting-api
docker rm greeting-api
docker run -d --name greeting-api old-image:version

# Git
git revert HEAD
git push
```

## Support

For deployment issues, please open an issue in the repository.