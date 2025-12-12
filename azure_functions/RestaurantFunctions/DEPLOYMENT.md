# RegisterRestaurant Azure Function - Deployment Guide

## ✅ Local Testing Complete

The function has been tested locally and is working! You can test it with:

```bash
curl -X POST "http://localhost:7071/api/RegisterRestaurant?restaurantName=Test%20Restaurant&deliveryArea=Central"
```

## Deploy to Azure

### Step 1: Get Your Resource Group and Storage Account

First, set your variables (replace with your actual values):

```bash
export resource=YOUR_RESOURCE_GROUP
export storageaccount=cgp1storage
export groupname=YOUR_GROUP_NAME
```

### Step 2: Create the Function App in Azure

```bash
az functionapp create \
  --consumption-plan-location westeurope \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --resource-group $resource \
  --name RegisterRestaurant${groupname} \
  --os-type linux \
  --storage-account ${storageaccount} \
  --disable-app-insights
```

### Step 3: Deploy the Function

```bash
cd "/Users/habibrahal/Documents/cloud computing/CloudComputing/azure_functions/RestaurantFunctions"
func azure functionapp publish RegisterRestaurant${groupname} --python
```

### Step 4: Configure Connection String in Azure

After deployment, you need to set the connection string in Azure Portal:

1. Go to Azure Portal → Your Function App → Configuration
2. Add a new application setting:
   - Name: `AzureWebJobsStorage`
   - Value: Your connection string (same as in local.settings.json)

Or use Azure CLI:

```bash
# Get your connection string first:
CONNECTION_STRING=$(az storage account show-connection-string --name ${storageaccount} --resource-group $resource --query connectionString -o tsv)

# Then set it:
az functionapp config appsettings set \
  --name RegisterRestaurant${groupname} \
  --resource-group $resource \
  --settings "AzureWebJobsStorage=$CONNECTION_STRING"
```

### Step 5: Test the Deployed Function

Get the function URL from Azure Portal:
- Go to Function App → Functions → RegisterRestaurant → "Get Function URL"
- Copy the URL and test with:

```bash
curl "https://registerrestaurant${groupname}.azurewebsites.net/api/RegisterRestaurant?restaurantName=TestRestaurant&deliveryArea=Central&code=YOUR_FUNCTION_KEY"
```

## Function Details

- **Table**: Restaurants
- **Required Parameters**: 
  - `restaurantName` (string)
  - `deliveryArea` (string: North, Central, or South)
- **Returns**: JSON with `ok`, `rowKey`, and `entity` fields

## Local Development

To run locally:

```bash
cd "/Users/habibrahal/Documents/cloud computing/CloudComputing/azure_functions/RestaurantFunctions"
source .venv/bin/activate
func start --port 7071
```

Then test in another terminal:
```bash
curl -X POST "http://localhost:7071/api/RegisterRestaurant?restaurantName=TestRestaurant&deliveryArea=Central"
```

