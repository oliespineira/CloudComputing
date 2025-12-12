# Milestone 2 Setup Instructions

## Connection String

Use this connection string for Azure Storage operations:

```bash
# Get your connection string using Azure CLI:
az storage account show-connection-string --name cgp1storage --resource-group CC_M_A_G1 --query connectionString -o tsv

# Then set it:
export AZURE_STORAGE_CONNECTION_STRING="<your-connection-string-here>"
```

**Note:** To get the latest connection string, use:
```bash
az storage account show-connection-string --name cgp1storage --resource-group <your-resource-group> --query connectionString -o tsv
```

## Data Population Status

✅ **Restaurants Table**: 30 restaurants inserted (10 per area: North, Central, South)
✅ **Meals Table**: ~150 meals inserted across all restaurants

## Running the Scripts

1. **Set the connection string:**
   ```bash
   export AZURE_STORAGE_CONNECTION_STRING="<connection-string>"
   ```

2. **Populate Restaurants:**
   ```bash
   cd milestone2
   python3 populate_restaurants_table.py
   ```

3. **Populate Meals:**
   ```bash
   python3 populate_meals.py
   ```

## Required Python Package

```bash
pip3 install azure-data-tables
```

## Next Steps

1. Deploy the Azure Functions (`RegisterRestaurant` and `RegisterMeal`)
2. Test the functions locally
3. Deploy to Azure Function App
4. Connect the frontend to these functions

