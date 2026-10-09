#!/bin/bash
# LUMIRA Zero-Downtime Deployment Script

set -e

echo "Starting LUMIRA deployment..."

# 1. Pull latest code
echo "Pulling latest code..."
git pull origin main

# 2. Build new images
echo "Building Docker images..."
docker-compose -f docker-compose.prod.yml build

# 3. Run database migrations
echo "Applying database migrations..."
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# 4. Restart services with zero-downtime using recreate
echo "Restarting services..."
docker-compose -f docker-compose.prod.yml up -d --no-deps --build

# 5. Clean up unused images and volumes
echo "Cleaning up..."
docker image prune -f

echo "Deployment completed successfully at $(date)!"
