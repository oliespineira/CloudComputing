#!/bin/bash

# Azure Storage Account name
STORAGE_ACCOUNT="cgp1storage"

# Get connection string
CONNECTION_STRING=$(az storage account show-connection-string \
  --name $STORAGE_ACCOUNT \
  --resource-group CC_M_A_G1 \
  --query connectionString -o tsv)

echo "Creating Azure Queues..."

# Create queues
az storage queue create --name deliveries-north --connection-string "$CONNECTION_STRING"
az storage queue create --name deliveries-central --connection-string "$CONNECTION_STRING"
az storage queue create --name deliveries-south --connection-string "$CONNECTION_STRING"

echo "Creating Azure Tables..."

# Create new tables
az storage table create --name Users --connection-string "$CONNECTION_STRING"
az storage table create --name Sessions --connection-string "$CONNECTION_STRING"
az storage table create --name Deliveries --connection-string "$CONNECTION_STRING"

echo "✅ Azure resources created successfully!"

