# ✅ RegisterRestaurant Function - Successfully Deployed!

## Deployment Details

- **Function App Name**: RegisterRestaurantG1
- **URL**: https://registerrestaurantg1.azurewebsites.net/api/registerrestaurant
- **Resource Group**: CC_M_A_G1
- **Storage Account**: cgp1storage
- **Status**: ✅ Deployed and Configured

## Function Key

Your function key can be retrieved from Azure Portal or using:
```bash
az functionapp function keys list --name RegisterRestaurantG1 --resource-group CC_M_A_G1 --function-name RegisterRestaurant --query "default" -o tsv
```

## How to Use

### Test the Function

```bash
curl -X POST "https://registerrestaurantg1.azurewebsites.net/api/registerrestaurant?restaurantName=MyRestaurant&deliveryArea=Central&code=YOUR_FUNCTION_KEY"
```

### Parameters

- **restaurantName** (required): Name of the restaurant
- **deliveryArea** (required): Delivery area (North, Central, or South)
- **code** (required): Function key for authentication

### Response

```json
{
  "ok": true,
  "rowKey": "uuid-here",
  "entity": {
    "PartitionKey": "Central",
    "RowKey": "uuid-here",
    "RestaurantName": "MyRestaurant",
    "DeliveryArea": "Central"
  }
}
```

## Next Steps

1. ✅ Function deployed
2. ✅ Connection string configured
3. ✅ Function tested
4. 🔄 You can now integrate this into your frontend!

## Frontend Integration

In your frontend code, you can call this function like:

```javascript
const response = await fetch(
  `https://registerrestaurantg1.azurewebsites.net/api/registerrestaurant?restaurantName=${name}&deliveryArea=${area}&code=YOUR_FUNCTION_KEY`
);
```

**Note**: For production, consider storing the function key securely or using Azure Key Vault.

