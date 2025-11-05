#!/bin/bash
set -e

# Configuration
REGISTRY="ghcr.io"
OWNER="mqharris"
REPO="knight-club"
TAG="${1:-dev}"
COMMIT_MSG="${2:-Update code}"

echo "🔨 Building and pushing images for knight-club (tag: $TAG)"
echo ""

# Git commit and push
echo "📝 Committing changes..."
git add .
git commit -m "$COMMIT_MSG" || echo "No changes to commit"
echo ""

echo "⬆️  Pushing to git..."
git push || echo "Nothing to push or push failed"
echo "✅ Git push complete"
echo ""

# Build and push backend
echo "📦 Building backend image..."
docker build -t $REGISTRY/$OWNER/$REPO/backend:$TAG ./backend
echo "✅ Backend image built"
echo ""

echo "⬆️  Pushing backend image..."
docker push $REGISTRY/$OWNER/$REPO/backend:$TAG
echo "✅ Backend image pushed"
echo ""

# Build and push webui
echo "📦 Building webui image..."
docker build -t $REGISTRY/$OWNER/$REPO/webui:$TAG ./webui
echo "✅ Webui image built"
echo ""

echo "⬆️  Pushing webui image..."
docker push $REGISTRY/$OWNER/$REPO/webui:$TAG
echo "✅ Webui image pushed"
echo ""

echo "🎉 All images built and pushed successfully!"
echo ""
echo "Images:"
echo "  - $REGISTRY/$OWNER/$REPO/backend:$TAG"
echo "  - $REGISTRY/$OWNER/$REPO/webui:$TAG"
