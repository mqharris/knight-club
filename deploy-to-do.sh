#!/bin/bash
# Deploy script for Digital Ocean droplet
# Run this script after pushing new images to deploy updates to the cluster

set -e

echo "🚀 Deploying Knight Club updates..."
echo ""

# Pull latest code
echo "📥 Pulling latest code from git..."
git pull origin k8s-init
echo "✅ Code updated"
echo ""

# Apply kustomize overlay (in case manifests changed)
echo "📦 Applying Kubernetes manifests..."
kubectl apply -k k8s/overlays/dev
echo "✅ Manifests applied"
echo ""

# Restart deployments to pull new images
echo "🔄 Restarting backend deployment..."
kubectl rollout restart deployment/backend -n knight-club
echo "✅ Backend restarted"
echo ""

echo "🔄 Restarting webui deployment..."
kubectl rollout restart deployment/webui -n knight-club
echo "✅ Webui restarted"
echo ""

# Wait for rollouts to complete
echo "⏳ Waiting for rollouts to complete..."
kubectl rollout status deployment/backend -n knight-club
kubectl rollout status deployment/webui -n knight-club
echo ""

# Show pod status
echo "📊 Current pod status:"
kubectl get pods -n knight-club
echo ""

echo "🎉 Deployment complete!"
echo ""
echo "Access your app at: http://$(curl -s ifconfig.me):30080"
