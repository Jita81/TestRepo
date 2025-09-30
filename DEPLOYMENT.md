# Deployment Guide

This guide covers deploying the Todo List application to various platforms.

## Table of Contents

1. [Local Deployment](#local-deployment)
2. [Docker Deployment](#docker-deployment)
3. [Heroku Deployment](#heroku-deployment)
4. [AWS Deployment](#aws-deployment)
5. [Digital Ocean Deployment](#digital-ocean-deployment)
6. [Production Best Practices](#production-best-practices)

---

## Local Deployment

### Prerequisites
- Node.js >= 14.0.0
- PostgreSQL >= 12.0
- npm or yarn

### Steps

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Create database**
   ```bash
   psql -U postgres
   CREATE DATABASE todolist;
   \q
   ```

4. **Run migrations**
   ```bash
   npm run db:migrate
   ```

5. **Start server**
   ```bash
   npm start
   ```

---

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Start all services**
   ```bash
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f app
   ```

3. **Stop services**
   ```bash
   docker-compose down
   ```

4. **Reset database**
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

### Manual Docker Build

1. **Build image**
   ```bash
   docker build -t todo-app:latest .
   ```

2. **Run container**
   ```bash
   docker run -d \
     --name todo-app \
     -p 3000:3000 \
     --env-file .env \
     todo-app:latest
   ```

---

## Heroku Deployment

### Prerequisites
- Heroku CLI installed
- Heroku account

### Steps

1. **Login to Heroku**
   ```bash
   heroku login
   ```

2. **Create app**
   ```bash
   heroku create your-todo-app-name
   ```

3. **Add PostgreSQL**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

4. **Set environment variables**
   ```bash
   heroku config:set NODE_ENV=production
   heroku config:set CORS_ORIGIN=https://your-todo-app-name.herokuapp.com
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

6. **Run migrations**
   ```bash
   heroku run npm run db:migrate
   ```

7. **Open app**
   ```bash
   heroku open
   ```

### Heroku Configuration

Create a `Procfile`:
```
web: node backend/server.js
```

---

## AWS Deployment

### Using AWS Elastic Beanstalk

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB**
   ```bash
   eb init -p node.js-18 todo-app
   ```

3. **Create environment**
   ```bash
   eb create todo-app-env
   ```

4. **Set environment variables**
   ```bash
   eb setenv NODE_ENV=production DB_HOST=your-rds-endpoint
   ```

5. **Deploy**
   ```bash
   eb deploy
   ```

### Using AWS EC2

1. **Launch EC2 instance** (Ubuntu 22.04 LTS)

2. **SSH into instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

3. **Install Node.js and PostgreSQL**
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs postgresql postgresql-contrib
   ```

4. **Clone repository**
   ```bash
   git clone your-repo-url
   cd todo-list-app
   ```

5. **Install dependencies**
   ```bash
   npm install
   ```

6. **Set up database**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE todolist;
   CREATE USER todouser WITH PASSWORD 'your-password';
   GRANT ALL PRIVILEGES ON DATABASE todolist TO todouser;
   \q
   ```

7. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env
   ```

8. **Install PM2**
   ```bash
   sudo npm install -g pm2
   ```

9. **Start application**
   ```bash
   pm2 start backend/server.js --name todo-app
   pm2 save
   pm2 startup
   ```

10. **Set up Nginx reverse proxy**
    ```bash
    sudo apt-get install nginx
    sudo nano /etc/nginx/sites-available/todo-app
    ```

    Add configuration:
    ```nginx
    server {
        listen 80;
        server_name your-domain.com;

        location / {
            proxy_pass http://localhost:3000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }
    }
    ```

    Enable site:
    ```bash
    sudo ln -s /etc/nginx/sites-available/todo-app /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx
    ```

---

## Digital Ocean Deployment

### Using App Platform

1. **Connect GitHub repository**

2. **Configure build settings**
   - Build Command: `npm install`
   - Run Command: `npm start`

3. **Add PostgreSQL database**

4. **Set environment variables**

5. **Deploy**

### Using Droplet

1. **Create Droplet** (Ubuntu 22.04)

2. **Follow AWS EC2 steps** above for SSH, installation, and setup

3. **Configure firewall**
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

---

## Production Best Practices

### Security

1. **Use HTTPS**
   - Install SSL certificate (Let's Encrypt)
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

2. **Environment Variables**
   - Never commit `.env` files
   - Use secure, random passwords
   - Rotate credentials regularly

3. **Database Security**
   - Use strong passwords
   - Limit network access
   - Enable SSL connections
   - Regular backups

4. **Rate Limiting**
   - Configure appropriate limits
   - Monitor for abuse
   - Implement IP blocking if needed

### Performance

1. **Connection Pooling**
   - Configure appropriate pool sizes
   - Monitor connection usage

2. **Caching**
   - Implement Redis for session storage
   - Cache frequent queries

3. **CDN**
   - Serve static files from CDN
   - Enable gzip compression

### Monitoring

1. **Application Monitoring**
   ```bash
   pm2 install pm2-logrotate
   pm2 set pm2-logrotate:max_size 10M
   pm2 set pm2-logrotate:retain 7
   ```

2. **Health Checks**
   - Monitor `/api/health` endpoint
   - Set up alerts for downtime

3. **Error Tracking**
   - Integrate Sentry or similar service
   - Monitor error rates

### Backup

1. **Database Backups**
   ```bash
   # Create backup script
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   pg_dump -U postgres todolist > backup_$DATE.sql
   
   # Schedule with cron
   0 2 * * * /path/to/backup.sh
   ```

2. **Backup Retention**
   - Keep daily backups for 7 days
   - Keep weekly backups for 4 weeks
   - Keep monthly backups for 1 year

### Scaling

1. **Horizontal Scaling**
   - Use load balancer
   - Run multiple app instances
   - Share session storage (Redis)

2. **Database Scaling**
   - Read replicas for read-heavy workloads
   - Connection pooling
   - Query optimization

### Maintenance

1. **Updates**
   ```bash
   # Pull latest code
   git pull origin main
   
   # Install dependencies
   npm install
   
   # Run migrations
   npm run db:migrate
   
   # Restart app
   pm2 restart todo-app
   ```

2. **Zero-Downtime Deployment**
   ```bash
   pm2 reload todo-app
   ```

3. **Monitoring Logs**
   ```bash
   pm2 logs todo-app
   pm2 monit
   ```

---

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check database credentials
   - Verify database is running
   - Check network connectivity

2. **Port Already in Use**
   ```bash
   lsof -ti:3000 | xargs kill -9
   ```

3. **Migration Failures**
   - Check database permissions
   - Verify schema.sql syntax
   - Check PostgreSQL logs

4. **Memory Issues**
   ```bash
   # Increase Node.js memory
   NODE_OPTIONS=--max_old_space_size=4096 npm start
   ```

---

## Support

For deployment issues:
- Check application logs
- Review database logs
- Verify environment variables
- Check firewall settings
- Monitor resource usage

---

**Good luck with your deployment! 🚀**