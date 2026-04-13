# Production Deployment Guide

## Pre-Deployment Checklist

- [ ] All tests passing (`pytest`)
- [ ] Model weights downloaded/trained
- [ ] `.env` configured with production values
- [ ] CORS origins restricted
- [ ] Rate limiting configured
- [ ] Authentication implemented
- [ ] Logging configured
- [ ] Health check endpoint tested
- [ ] Load testing performed
- [ ] Monitoring/alerting setup

## Deployment Options

### Option 1: Linux Server (Gunicorn + Nginx)

#### Step 1: Setup Server
```bash
# SSH into your server
ssh user@your-server.com

# Create app directory
mkdir -p /var/www/gan-api
cd /var/www/gan-api

# Clone or copy your code
git clone <your-repo> .
# or
scp -r gan_api/* user@server:/var/www/gan-api/
```

#### Step 2: Setup Python Environment
```bash
# Install Python 3.11 (if needed)
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 3: Configure Gunicorn
Create `/etc/systemd/system/gan-api.service`:
```ini
[Unit]
Description=GAN Backend API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/gan-api
Environment="PATH=/var/www/gan-api/venv/bin"
ExecStart=/var/www/gan-api/venv/bin/gunicorn \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind unix:/var/www/gan-api/gan-api.sock \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    app.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Step 4: Configure Nginx
Create `/etc/nginx/sites-available/gan-api`:
```nginx
upstream gan-api {
    server unix:/var/www/gan-api/gan-api.sock fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;

    # Gzip compression
    gzip on;
    gzip_types application/json;
    gzip_min_length 1000;

    location / {
        proxy_pass http://gan-api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        
        # Timeouts for long-running requests
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

#### Step 5: Enable and Start Services
```bash
# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/gan-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Start GAN API service
sudo systemctl enable gan-api.service
sudo systemctl start gan-api.service

# Check status
sudo systemctl status gan-api.service
```

### Option 2: Docker

#### Build Image
```bash
docker build -t gan-backend:1.0.0 .
docker tag gan-backend:1.0.0 your-registry/gan-backend:1.0.0
docker tag gan-backend:1.0.0 your-registry/gan-backend:latest
```

#### Push to Registry
```bash
docker login your-registry
docker push your-registry/gan-backend:1.0.0
docker push your-registry/gan-backend:latest
```

#### Deploy Standalone
```bash
docker run -d \
    --name gan-api \
    --gpus all \
    -p 8000:8000 \
    -v /data/weights:/app/weights \
    -e DEVICE=cuda \
    --restart unless-stopped \
    your-registry/gan-backend:latest
```

### Option 3: Kubernetes

#### Create Namespace
```bash
kubectl create namespace gan-api
```

#### Create ConfigMap
```bash
kubectl create configmap gan-config \
    --from-literal=DEVICE=cuda \
    --from-literal=IMAGE_SIZE=256 \
    -n gan-api
```

#### Deploy with Helm
See `helm/values.yaml` configuration

```bash
helm install gan-api ./helm -n gan-api
```

### Option 4: Cloud Platforms

#### AWS Elastic Container Service (ECS)
```bash
# Push image to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/gan-backend:latest

# Create ECS task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Run service
aws ecs create-service --cluster production --service-name gan-api ...
```

#### Google Cloud Run (CPU/GPU support)
```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT-ID/gan-backend

# Deploy
gcloud run deploy gan-api \
    --image gcr.io/PROJECT-ID/gan-backend \
    --platform managed \
    --region us-central1 \
    --memory 8Gb \
    --gpu
```

#### Heroku
```bash
# Create Heroku app
heroku create gan-api

# Add GPU plugin (if available)
heroku buildpacks:add heroku-community/apt
heroku buildpacks:add heroku/python

# Deploy
git push heroku main
```

## Monitoring & Logging

### Prometheus Metrics
Add to `app/main.py`:
```python
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### ELK Stack Integration
```yaml
# docker-compose.yml addition
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
  environment:
    - discovery.type=single-node

logstash:
  image: docker.elastic.co/logstash/logstash:8.0.0
  volumes:
    - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

kibana:
  image: docker.elastic.co/kibana/kibana:8.0.0
  ports:
    - "5601:5601"
```

### Application Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("API started successfully")
```

## Performance Tuning

### Nginx Optimization
```nginx
# Increase worker connections
worker_connections 1024;

# Connection pooling
upstream gan-api {
    keepalive 32;
}

# HTTP/2 multiplexing
listen 443 ssl http2;

# Caching
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=gan-cache:10m;
proxy_cache gan-cache;
proxy_cache_key "$scheme$request_method$host$request_uri";
```

### Database Connection Pooling (if needed)
```python
# Use asyncpg for async database access
import asyncpg

pool = asyncpg.create_pool('postgresql://user:password@host/db')
```

### PyTorch GPU Optimization
```python
import torch

# Enable TF32 precision (faster on A100)
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

# Cudnn auto-tuner
torch.backends.cudnn.benchmark = True
```

## Scaling

### Horizontal Scaling
- Load balance across multiple instances with Nginx
- Use database for shared state (if needed)
- Cache CLIP embeddings in Redis

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379)

def get_embedding(prompt: str):
    cached = redis_client.get(f"embedding:{prompt}")
    if cached:
        return cached
    
    embedding = encode_text(prompt)
    redis_client.setex(f"embedding:{prompt}", 3600, embedding)
    return embedding
```

### Vertical Scaling
- Upgrade GPU (V100 → A100)
- Increase RAM
- Use faster storage (NVMe SSD)

## Security Hardening

### API Security
```python
# Rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/generate")
@limiter.limit("5/minute")
async def generate_image(...):
    pass

# CORS
CORSMiddleware(
    app,
    allow_origins=["https://yourdomain.com"],
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)

# Authentication
from fastapi.security import HTTPBearer
security = HTTPBearer()

@router.post("/generate")
async def generate_image(
    request: GenerateRequest,
    credentials: HTTPAuthCredentials = Depends(security),
):
    pass
```

### Infrastructure Security
- Use VPC/Security groups
- Restrict SSH access
- Enable firewall
- Use Let's Encrypt SSL/TLS
- Enable HTTPS only

### Secrets Management
- Use environment variables (not hardcoded)
- Use AWS Secrets Manager, HashiCorp Vault, etc.
- Rotate API keys regularly

```bash
# Using .env (never commit to git)
CLIP_MODEL_NAME=openai/clip-vit-base-patch32
API_KEY=your-secret-key-here
```

## Disaster Recovery

### Backup Strategy
```bash
# Backup model weights
aws s3 sync ./weights s3://my-bucket/gan-api-backup/weights/

# Backup entire app every week
tar -czf gan-api-backup-$(date +%Y%m%d).tar.gz app/
```

### Health Checks
```bash
# Monitor health endpoint
curl -f http://localhost:8000/api/v1/health || trigger_alert

# Use monitoring tools (Datadog, New Relic, etc.)
```

## Maintenance Windows

### Zero-Downtime Deployment
```bash
# Blue-Green deployment
# 1. Deploy new version to separate instance
# 2. Test thoroughly
# 3. Update load balancer to point to new instance
# 4. Keep old instance running for instant rollback

# Or use rolling updates with Kubernetes
kubectl set image deployment/gan-api \
    gan-api=your-registry/gan-backend:v2
```

## Cost Optimization

- Use spot instances for development
- Schedule auto-scaling for off-peak hours
- Use smaller models during low traffic
- Implement request caching

## Links & Resources

- [Gunicorn Configuration](https://docs.gunicorn.org/en/latest/design.html)
- [Nginx Best Practices](https://nginx.org/en/docs/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [PyTorch Performance Tuning](https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html)

---

**Ready to deploy! 🚀**
