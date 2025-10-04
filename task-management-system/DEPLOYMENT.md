# 🚀 Deployment Guide

Complete guide for deploying the Task Management System to production.

## AWS Deployment

### Prerequisites

- AWS Account
- AWS CLI configured
- Domain name (optional but recommended)
- SSL certificate (AWS Certificate Manager)

### Architecture Overview

```
┌─────────────┐
│ CloudFront  │ ◄── Frontend (S3)
└──────┬──────┘
       │
┌──────▼──────┐
│     ALB     │ ◄── Backend (ECS)
└──────┬──────┘
       │
┌──────┴──────┬──────────┬──────────┐
│     RDS     │ ElastiCache│  ECS    │
│ PostgreSQL  │   Redis    │ Cluster │
└─────────────┴──────────┴──────────┘
```

### Step 1: Database Setup (RDS)

1. **Create PostgreSQL RDS Instance:**
```bash
aws rds create-db-instance \
  --db-instance-identifier taskman-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --master-username postgres \
  --master-user-password YOUR_PASSWORD \
  --allocated-storage 20 \
  --backup-retention-period 7 \
  --vpc-security-group-ids sg-xxxxx
```

2. **Run database schema:**
```bash
psql -h your-rds-endpoint.amazonaws.com \
     -U postgres \
     -d task_management \
     -f database/schema.sql
```

### Step 2: Redis Setup (ElastiCache)

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id taskman-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1 \
  --security-group-ids sg-xxxxx
```

### Step 3: Backend Deployment (ECS)

1. **Build and push Docker image:**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URI

# Build image
cd backend
docker build -t taskman-backend .

# Tag image
docker tag taskman-backend:latest YOUR_ECR_URI/taskman-backend:latest

# Push to ECR
docker push YOUR_ECR_URI/taskman-backend:latest
```

2. **Create ECS Task Definition:**
```json
{
  "family": "taskman-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "YOUR_ECR_URI/taskman-backend:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "NODE_ENV",
          "value": "production"
        },
        {
          "name": "DB_HOST",
          "value": "your-rds-endpoint.amazonaws.com"
        },
        {
          "name": "REDIS_HOST",
          "value": "your-elasticache-endpoint.amazonaws.com"
        }
      ],
      "secrets": [
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:db-password"
        },
        {
          "name": "JWT_SECRET",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:jwt-secret"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/taskman-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

3. **Create ECS Service:**
```bash
aws ecs create-service \
  --cluster taskman-cluster \
  --service-name taskman-backend-service \
  --task-definition taskman-backend \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=backend,containerPort=3000"
```

### Step 4: Frontend Deployment (S3 + CloudFront)

1. **Build frontend:**
```bash
cd frontend
npm run build
```

2. **Create S3 bucket:**
```bash
aws s3 mb s3://taskman-frontend --region us-east-1
```

3. **Configure bucket for static hosting:**
```bash
aws s3 website s3://taskman-frontend \
  --index-document index.html \
  --error-document index.html
```

4. **Upload files:**
```bash
aws s3 sync dist/ s3://taskman-frontend --acl public-read
```

5. **Create CloudFront distribution:**
```json
{
  "CallerReference": "taskman-frontend-distribution",
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-taskman-frontend",
        "DomainName": "taskman-frontend.s3.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-taskman-frontend",
    "ViewerProtocolPolicy": "redirect-to-https",
    "Compress": true,
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": { "Forward": "none" }
    }
  },
  "Enabled": true,
  "DefaultRootObject": "index.html",
  "CustomErrorResponses": {
    "Quantity": 1,
    "Items": [
      {
        "ErrorCode": 404,
        "ResponsePagePath": "/index.html",
        "ResponseCode": "200"
      }
    ]
  }
}
```

### Step 5: Configure Domain & SSL

1. **Request SSL certificate in ACM:**
```bash
aws acm request-certificate \
  --domain-name yourdomain.com \
  --subject-alternative-names www.yourdomain.com api.yourdomain.com \
  --validation-method DNS
```

2. **Configure Route 53:**
- Create A record for frontend pointing to CloudFront
- Create A record for API pointing to ALB

### Step 6: Environment Variables & Secrets

Store sensitive data in AWS Secrets Manager:

```bash
# Database password
aws secretsmanager create-secret \
  --name taskman/db-password \
  --secret-string "your-db-password"

# JWT secrets
aws secretsmanager create-secret \
  --name taskman/jwt-secret \
  --secret-string "your-jwt-secret-min-32-chars"

aws secretsmanager create-secret \
  --name taskman/jwt-refresh-secret \
  --secret-string "your-jwt-refresh-secret"
```

## Alternative Deployments

### Heroku Deployment

1. **Install Heroku CLI**
2. **Create app:**
```bash
heroku create taskman-backend
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev
```

3. **Deploy:**
```bash
cd backend
git push heroku main
```

4. **Run migrations:**
```bash
heroku run psql $DATABASE_URL < ../database/schema.sql
```

### DigitalOcean Deployment

1. **Create Droplet** (Ubuntu 22.04)
2. **Install dependencies:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

3. **Deploy with Docker Compose:**
```bash
scp docker-compose.yml root@your-server-ip:/root/
ssh root@your-server-ip
docker-compose up -d
```

### Vercel (Frontend Only)

```bash
cd frontend
npm i -g vercel
vercel --prod
```

## Monitoring & Logging

### CloudWatch Setup

1. **Create log groups:**
```bash
aws logs create-log-group --log-group-name /ecs/taskman-backend
aws logs create-log-group --log-group-name /ecs/taskman-frontend
```

2. **Set up alarms:**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name taskman-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

### Application Monitoring

- **Sentry** for error tracking
- **DataDog** for APM
- **New Relic** for full-stack monitoring

## Backup & Recovery

### Database Backups

1. **Enable automated backups:**
```bash
aws rds modify-db-instance \
  --db-instance-identifier taskman-db \
  --backup-retention-period 30 \
  --preferred-backup-window "03:00-04:00"
```

2. **Manual backup:**
```bash
aws rds create-db-snapshot \
  --db-instance-identifier taskman-db \
  --db-snapshot-identifier taskman-backup-$(date +%Y%m%d)
```

### Redis Backups

ElastiCache automatically backs up Redis with snapshots.

## Scaling

### Horizontal Scaling (ECS)

```bash
aws ecs update-service \
  --cluster taskman-cluster \
  --service taskman-backend-service \
  --desired-count 5
```

### Auto Scaling

```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/taskman-cluster/taskman-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10
```

## Security Checklist

- [ ] Use HTTPS everywhere
- [ ] Rotate secrets regularly
- [ ] Enable VPC for RDS and ElastiCache
- [ ] Use security groups to restrict access
- [ ] Enable CloudWatch logs
- [ ] Set up AWS WAF for DDoS protection
- [ ] Use IAM roles with least privilege
- [ ] Enable MFA for AWS account
- [ ] Regular security audits
- [ ] Keep dependencies updated

## Cost Optimization

- Use t3.micro instances for development
- Enable auto-scaling
- Use reserved instances for production
- Set up billing alerts
- Clean up unused resources
- Use S3 lifecycle policies

## Troubleshooting

### WebSocket Connection Issues

1. Check ALB configuration for WebSocket support
2. Ensure sticky sessions are enabled
3. Verify security group rules

### Database Connection Issues

1. Check security group inbound rules
2. Verify RDS is in correct VPC
3. Test connection from ECS task

### Redis Connection Issues

1. Verify ElastiCache security group
2. Check if Redis is in correct VPC subnet
3. Test connectivity from backend container

---

For additional help, consult [AWS Documentation](https://docs.aws.amazon.com/) or open an issue.
