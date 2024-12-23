# Video Downloader Azure Function

This Azure Function automatically downloads completed videos from Hedra and stores them in Azure Blob Storage. It runs every hour to check for new completed videos.

## Setup Instructions

1. Create Azure Resources:
```bash
# Create a Resource Group
az group create --name mec-video-group --location eastus

# Create a Storage Account
az storage account create --name mecvideostorage --location eastus --resource-group mec-video-group --sku Standard_LRS

# Create a Function App
az functionapp create --name mec-video-downloader --storage-account mecvideostorage --consumption-plan-location eastus --resource-group mec-video-group --runtime python --runtime-version 3.9 --functions-version 4
```

2. Create a Blob Storage Container:
   - Go to Azure Portal > Storage Account > Containers
   - Create a new container named 'generated-videos'
   - Set access level to 'Container (anonymous read access for containers and blobs)'

3. Configure Function App Settings:
```bash
# Set required environment variables
az functionapp config appsettings set --name mec-video-downloader --resource-group mec-video-group --settings \
    HEDRA_API_KEY="your_hedra_api_key" \
    DB_PATH="/path/to/images.db" \
    STORAGE_CONNECTION_STRING="your_storage_connection_string"
```

4. Deploy the Function:
```bash
# Navigate to the azure_function directory
cd azure_function

# Deploy using Azure Functions Core Tools
func azure functionapp publish mec-video-downloader
```

5. Update Docker Configuration:
   - Add Azure Storage connection to your docker-compose.yml:
```yaml
services:
  web:
    environment:
      - AZURE_STORAGE_CONNECTION_STRING=your_storage_connection_string
    volumes:
      - ./instance:/app/instance  # For SQLite database access
```

6. Update Gallery Template:
   - The video URLs in the database will now point to Azure Blob Storage
   - The gallery will automatically use these URLs when displaying videos

## How It Works

1. Every hour, the function:
   - Queries the SQLite database for completed videos without local paths
   - Gets fresh video URLs from Hedra API
   - Downloads videos and uploads them to Azure Blob Storage
   - Updates the database with new video URLs

2. The web application:
   - Continues to work normally
   - Videos are served from Azure Blob Storage instead of local storage
   - No changes needed to the web interface

## Monitoring

Monitor the function's execution:
```bash
# View function logs
az functionapp logs tail --name mec-video-downloader --resource-group mec-video-group
```

## Troubleshooting

1. If videos aren't downloading:
   - Check function logs for errors
   - Verify environment variables are set correctly
   - Ensure the function has access to your SQLite database
   - Check Hedra API key permissions

2. If videos aren't displaying:
   - Verify blob storage container permissions
   - Check the video URLs in the database
   - Ensure the storage account is accessible

## Notes

- The function runs every hour (configurable in function.json)
- Videos are stored with 1-year SAS tokens
- The function requires access to your SQLite database
- Consider backing up your database regularly
