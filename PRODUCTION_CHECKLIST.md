# ScrapeMaster Production Deployment Checklist

## Pre-Deployment

### Security
- [ ] Generate strong SECRET_KEY for production
- [ ] Enable HTTPS with valid SSL certificates
- [ ] Configure firewall rules (only expose 80/443)
- [ ] Set up rate limiting for API endpoints
- [ ] Enable CORS with specific allowed origins
- [ ] Review and remove all debug code
- [ ] Scan dependencies for vulnerabilities: `pip audit`

### Environment Setup
- [ ] Create `.env` file from `.env.production` template
- [ ] Configure all required environment variables
- [ ] Set up production database (PostgreSQL recommended)
- [ ] Configure Redis for caching and sessions
- [ ] Set up proxy service credentials (ScraperAPI, BrightData, etc.)

### Monitoring & Logging
- [ ] Configure Sentry for error tracking
- [ ] Set up log rotation (logrotate)
- [ ] Configure application metrics collection
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)
- [ ] Configure backup automation
- [ ] Set up alerting for critical errors

### Performance
- [ ] Enable caching (Redis)
- [ ] Configure CDN for static assets
- [ ] Optimize database queries and add indexes
- [ ] Set appropriate connection pool sizes
- [ ] Configure autoscaling rules

## Deployment Steps

### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose -y

# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Application Deployment
```bash
# Clone repository
git clone https://github.com/yourorg/scrapemaster.git
cd scrapemaster

# Create environment file
cp .env.production .env
# Edit .env with production values

# Build and start services
docker-compose build
docker-compose up -d

# Check logs
docker-compose logs -f app
```

### 3. SSL Setup (with Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificates
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### 4. Database Migration
```bash
# Run database migrations
docker-compose exec app python manage.py migrate

# Create superuser
docker-compose exec app python manage.py createsuperuser
```

## Post-Deployment

### Verification
- [ ] Health check endpoint returns 200: `curl https://yourdomain.com/health`
- [ ] Can create and log into user account
- [ ] Can add and monitor a test target
- [ ] Proxy rotation is working
- [ ] Email notifications are sent
- [ ] Metrics are being collected
- [ ] Backups are running

### Security Hardening
- [ ] Run security scan: `docker scan scrapemaster-app`
- [ ] Check SSL rating: https://www.ssllabs.com/ssltest/
- [ ] Verify no sensitive data in logs
- [ ] Ensure debug mode is disabled
- [ ] Check file permissions

### Performance Testing
- [ ] Load test with expected traffic
- [ ] Monitor resource usage under load
- [ ] Verify autoscaling triggers
- [ ] Check response times

## Maintenance

### Regular Tasks
- Daily: Check error logs and metrics
- Weekly: Review performance metrics
- Monthly: Update dependencies
- Quarterly: Security audit

### Backup Verification
- [ ] Test database restore procedure
- [ ] Verify backup integrity
- [ ] Document recovery procedures

### Monitoring Dashboards
- Application metrics: http://yourdomain.com/metrics
- Server metrics: Configure Grafana/Prometheus
- Error tracking: Sentry dashboard
- Uptime: UptimeRobot dashboard

## Rollback Plan

If issues occur:
1. Keep previous Docker images tagged
2. Database backup before migration
3. Quick rollback: `docker-compose down && docker-compose up -d --scale app=0`
4. Restore from backup if needed

## Support Contacts

- DevOps Lead: devops@yourcompany.com
- On-call Engineer: +1-xxx-xxx-xxxx
- Escalation: engineering-lead@yourcompany.com

## Known Issues

1. **Playwright on Linux**: Requires additional dependencies
   ```bash
   docker-compose exec app playwright install-deps
   ```

2. **Proxy Connection**: Some proxy providers require IP whitelisting

3. **Memory Usage**: Monitor for memory leaks in long-running scrapers

## Emergency Procedures

### High CPU/Memory
```bash
# Restart app container
docker-compose restart app

# Scale down if needed
docker-compose scale app=1
```

### Database Issues
```bash
# Check connections
docker-compose exec db psql -U scrapemaster -c "SELECT count(*) FROM pg_stat_activity;"

# Kill idle connections
docker-compose exec db psql -U scrapemaster -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle';"
```

### Complete System Recovery
```bash
# Stop all services
docker-compose down

# Restore from backup
docker-compose exec db psql -U scrapemaster < /backups/latest.sql

# Restart
docker-compose up -d
``` 