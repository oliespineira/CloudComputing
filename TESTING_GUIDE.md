# Testing Azure Functions Guide

## Quick Start

### Option 1: Test Locally (Recommended First)

1. **Start the function locally:**
```bash
cd backend
func start
```

2. **In another terminal, run the test script:**
```bash
chmod +x test_functions.sh
./test_functions.sh local
```

3. **Or test manually with curl:**
```bash
curl -X POST "http://localhost:7071/api/RegisterMeal" \
  -H "Content-Type: application/json" \
  -d '{
    "restaurantName": "Mario Pizza",
    "dishName": "Margherita",
    "description": "Classic pizza",
    "price": 12.99,
    "prepTime": 25,
    "area": "Central"
  }'
```

### Option 2: Test Deployed Functions

1. **Get your function URL from Azure Portal:**
   - Go to Azure Portal → Your Function App → Functions → RegisterMeal
   - Click "Get Function URL"
   - Copy the URL (it includes the function key)

2. **Test with curl:**
```bash
curl -X POST "https://YOUR_FUNCTION_APP.azurewebsites.net/api/RegisterMeal?code=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "restaurantName": "Mario Pizza",
    "dishName": "Margherita",
    "description": "Classic pizza",
    "price": 12.99,
    "prepTime": 25,
    "area": "Central"
  }'
```

## Verify Data Was Saved

### Method 1: Azure Portal (Visual)
1. Go to Azure Portal → Storage Account (`cgp1storage`)
2. Click "Tables" → "Meals"
3. You should see your test meal

### Method 2: Python Script
```bash
cd backend
python3 -c "
from azure.data.tables import TableClient
import os
from dotenv import load_dotenv

# Load from local.settings.json equivalent
connection_string = 'YOUR_CONNECTION_STRING_HERE'
client = TableClient.from_connection_string(
    conn_str=connection_string,
    table_name='Meals'
)

print('Meals in table:')
for entity in client.list_entities():
    print(f\"  {entity.get('DishName')} - {entity.get('RestaurantName')} - {entity.get('PartitionKey')}\")
"
```

## Expected Responses

### ✅ Success Response (200):
```json
{
  "success": true,
  "message": "Meal registered successfully",
  "mealId": "uuid-here"
}
```

### ❌ Error Responses:

**Missing fields (400):**
```json
{
  "error": "Missing required fields"
}
```

**Invalid JSON (400):**
```json
{
  "error": "Request body must be valid JSON"
}
```

**Server error (500):**
```json
{
  "error": "Server configuration error"
}
```
(Usually means connection string not set)

## Troubleshooting

### Function won't start locally:
- Check Python version: `python3 --version` (needs 3.8+)
- Install dependencies: `cd backend && pip install -r requirements.txt`
- Check `local.settings.json` exists and has connection string

### Function returns 500 error:
- Check `AZURE_STORAGE_CONNECTION_STRING` is set in `local.settings.json`
- Verify the connection string is valid
- Check Azure Storage account exists and table "Meals" is created

### Function deployed but not working:
- Check function logs in Azure Portal
- Verify connection string is set in Function App settings
- Check CORS settings if calling from browser

## Testing from Browser Console

If your function is deployed and CORS is enabled:

```javascript
fetch('https://YOUR_FUNCTION_APP.azurewebsites.net/api/RegisterMeal?code=YOUR_KEY', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    restaurantName: "Test Restaurant",
    dishName: "Test Dish",
    description: "Test description",
    price: 10.99,
    prepTime: 20,
    area: "Central"
  })
})
.then(res => res.json())
.then(data => console.log('Success:', data))
.catch(err => console.error('Error:', err));
```

