# How to Check if Your Azure Function Worked

## Method 1: Azure Portal (Easiest - Visual)

1. **Go to Azure Portal**: https://portal.azure.com
2. **Navigate to your Storage Account**:
   - Search for "cgp1storage" in the top search bar
   - Click on your storage account
3. **Open Table Storage**:
   - In the left menu, click on "Tables" (under Data storage)
   - Click on the "Restaurants" table
4. **View the Data**:
   - You should see all restaurants listed
   - Look for "TestDeployedRestaurant" in the Central area
   - You can see all columns: PartitionKey, RowKey, RestaurantName, DeliveryArea

## Method 2: Azure Portal - Function App Logs

1. **Go to Azure Portal**: https://portal.azure.com
2. **Navigate to Function App**:
   - Search for "RegisterRestaurantG1"
   - Click on it
3. **View Logs**:
   - Click on "Functions" in the left menu
   - Click on "RegisterRestaurant"
   - Click on "Monitor" tab
   - You'll see execution logs and can see if the function ran successfully

## Method 3: Using Azure CLI (Command Line)

```bash
# Check the function app logs
az functionapp log tail --name RegisterRestaurantG1 --resource-group CC_M_A_G1
```

## Method 4: Test the Function Again

You can test it again and see the response:

```bash
curl -X POST "https://registerrestaurantg1.azurewebsites.net/api/registerrestaurant?restaurantName=AnotherTest&deliveryArea=North&code=YOUR_FUNCTION_KEY"
```

If you get a response like:
```json
{"ok": true, "rowKey": "...", "entity": {...}}
```

Then it worked! ✅

## Method 5: Check Table via Python Script

Run this to see all restaurants:

```bash
cd milestone2
export AZURE_STORAGE_CONNECTION_STRING="your_connection_string"
python3 -c "
from azure.data.tables import TableClient
import os
client = TableClient.from_connection_string(
    conn_str=os.getenv('AZURE_STORAGE_CONNECTION_STRING'), 
    table_name='Restaurants'
)
for entity in client.list_entities():
    print(f'{entity.get(\"RestaurantName\")} - {entity.get(\"DeliveryArea\")}')
"
```

## What to Look For

✅ **Success indicators**:
- Function returns `{"ok": true, ...}`
- Restaurant appears in the Restaurants table in Azure Portal
- No error messages in the function logs
- Status code 201 (Created) in the response

❌ **Failure indicators**:
- Error messages in the response
- Status code 400, 500, etc.
- Restaurant doesn't appear in the table
- Authentication errors

