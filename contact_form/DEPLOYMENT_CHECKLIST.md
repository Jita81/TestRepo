# Deployment Checklist

Use this checklist to ensure your contact form is properly configured for production deployment.

## Pre-Deployment

### Environment Setup
- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] All dependencies installed from `requirements.txt`
- [ ] Tests passing (`pytest tests/ -v`)

### Configuration

#### CORS Settings (`api.py`)
- [ ] Update `allow_origins` to specific domains (not `["*"]`)
- [ ] Set appropriate `allow_methods` (recommend `["POST"]` only)
- [ ] Configure `allow_credentials` based on auth requirements

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)
```

#### API Endpoint (`static/contact_form.js`)
- [ ] Update `API_ENDPOINT` to production URL

```javascript
const CONFIG = {
    API_ENDPOINT: 'https://api.yourdomain.com/api/contact',
    // ...
};
```

### Security

- [ ] Review and test all validation rules
- [ ] Implement rate limiting (see README.md)
- [ ] Add HTTPS/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up CSRF protection if needed
- [ ] Review CORS policy
- [ ] Implement request timeout limits
- [ ] Add request size limits

### Email Integration

- [ ] Choose email service (SendGrid, AWS SES, SMTP)
- [ ] Set up email templates
- [ ] Configure environment variables for API keys
- [ ] Test email delivery
- [ ] Set up email notifications for submissions
- [ ] Configure reply-to addresses

### Database (Optional)

- [ ] Choose database (PostgreSQL, MongoDB, etc.)
- [ ] Set up database connection
- [ ] Create database schema/tables
- [ ] Configure database migrations
- [ ] Set up database backups
- [ ] Test database connectivity

### Monitoring & Logging

- [ ] Configure structured logging
- [ ] Set up log aggregation (ELK, CloudWatch, etc.)
- [ ] Configure error tracking (Sentry, Rollbar, etc.)
- [ ] Set up performance monitoring
- [ ] Configure health check monitoring
- [ ] Set up alerting for failures

## Deployment Options

### Option 1: Docker

1. Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. Build and run:
```bash
docker build -t contact-form .
docker run -p 8000:8000 contact-form
```

**Checklist**:
- [ ] Dockerfile created
- [ ] Docker image builds successfully
- [ ] Container runs successfully
- [ ] Health check passes
- [ ] Environment variables configured
- [ ] Volumes configured for persistence

### Option 2: Cloud Platform (AWS, GCP, Azure)

**AWS Elastic Beanstalk**:
- [ ] Create `Procfile`: `web: uvicorn api:app --host 0.0.0.0 --port 8000`
- [ ] Configure environment variables
- [ ] Set up RDS for database (if needed)
- [ ] Configure security groups
- [ ] Set up CloudWatch logging

**Google Cloud Run**:
- [ ] Dockerfile created
- [ ] Cloud Build configured
- [ ] Service deployed
- [ ] Custom domain configured
- [ ] Monitoring enabled

**Azure App Service**:
- [ ] Create `startup.sh`
- [ ] Configure app settings
- [ ] Set up Application Insights
- [ ] Configure scaling rules

### Option 3: VPS (DigitalOcean, Linode, etc.)

1. Server setup:
```bash
# Install dependencies
sudo apt update
sudo apt install python3.11 python3-pip nginx certbot

# Clone repository
git clone <your-repo>
cd contact_form

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with systemd
sudo nano /etc/systemd/system/contact-form.service
```

2. Create systemd service:
```ini
[Unit]
Description=Contact Form API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/contact_form
Environment="PATH=/var/www/contact_form/venv/bin"
ExecStart=/var/www/contact_form/venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

**Checklist**:
- [ ] Server provisioned
- [ ] Dependencies installed
- [ ] Code deployed
- [ ] Service configured
- [ ] Nginx configured as reverse proxy
- [ ] SSL/TLS certificate installed
- [ ] Service starts on boot
- [ ] Logs configured

## Post-Deployment

### Testing

- [ ] Test form submission from production frontend
- [ ] Test validation errors
- [ ] Test success messages
- [ ] Test email delivery (if configured)
- [ ] Test on multiple browsers (Chrome, Firefox, Safari, Edge)
- [ ] Test on mobile devices
- [ ] Test error handling (network failures, server errors)
- [ ] Load testing (if expecting high traffic)

### Performance

- [ ] Response times acceptable (< 500ms)
- [ ] Form loads quickly
- [ ] No console errors in browser
- [ ] API documentation accessible
- [ ] Health check endpoint responding

### Monitoring Setup

- [ ] Uptime monitoring configured
- [ ] Error rate alerts set up
- [ ] Performance dashboards created
- [ ] Log aggregation working
- [ ] Backup jobs scheduled

### Documentation

- [ ] Update README with production URLs
- [ ] Document environment variables
- [ ] Create runbook for common issues
- [ ] Document deployment process
- [ ] Update API documentation

## Environment Variables

Create a `.env` file (DO NOT commit to git):

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=production

# CORS Settings
ALLOWED_ORIGINS=https://yourdomain.com

# Email Service
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=your_api_key_here
FROM_EMAIL=noreply@yourdomain.com
TO_EMAIL=support@yourdomain.com

# Database (if using)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Logging
LOG_LEVEL=INFO
SENTRY_DSN=your_sentry_dsn_here

# Rate Limiting
RATE_LIMIT_PER_MINUTE=5
```

## Nginx Configuration Example

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static {
        alias /var/www/contact_form/static;
        expires 30d;
    }

    # Health check
    location /api/health {
        proxy_pass http://localhost:8000/api/health;
        access_log off;
    }
}
```

## Rollback Plan

- [ ] Previous version tagged in git
- [ ] Database backup created
- [ ] Rollback procedure documented
- [ ] Team notified of deployment

## Production Launch

- [ ] All checklist items completed
- [ ] Stakeholders notified
- [ ] Team on standby for issues
- [ ] Monitoring dashboards open
- [ ] Communication channels ready

## Maintenance

### Weekly
- [ ] Review error logs
- [ ] Check submission volume
- [ ] Review response times

### Monthly
- [ ] Update dependencies
- [ ] Review and update documentation
- [ ] Analyze usage patterns
- [ ] Security audit

### Quarterly
- [ ] Load testing
- [ ] Disaster recovery drill
- [ ] Review and update monitoring
- [ ] Performance optimization review

## Common Issues & Solutions

### High Error Rate
- Check logs for error patterns
- Verify database connectivity
- Check email service status
- Review rate limiting settings

### Slow Response Times
- Check database query performance
- Review API response times
- Check network latency
- Scale horizontally if needed

### Form Not Submitting
- Check CORS configuration
- Verify API endpoint URL
- Check browser console for errors
- Test API directly with curl

## Support Contacts

- **Technical Lead**: [Name/Email]
- **DevOps**: [Name/Email]
- **On-Call**: [Phone/Pager]

---

**Deployment Date**: _______________
**Deployed By**: _______________
**Version**: _______________