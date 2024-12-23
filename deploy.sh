#!/bin/bash

# Variables
ACR_NAME="acrallupregistry"
IMAGE_NAME="myapp"
TAG="latest"
APP_SERVICE="makemecsaywhat"
RESOURCE_GROUP="rg-tribes"

# Rebuild Docker image
docker build -t $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG .

# Log in to Azure Container Registry
az acr login --name $ACR_NAME

# Push the image to Azure Container Registry
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG

# Restart Azure App Service to deploy the new image
az webapp restart --name $APP_SERVICE --resource-group $RESOURCE_GROUP

echo "Deployment completed successfully!"