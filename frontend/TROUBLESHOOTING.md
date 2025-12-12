# Troubleshooting Network Errors

## If you're getting a network error:

### 1. Check Browser Console
Open your browser's Developer Tools (F12) and check the Console tab for detailed error messages.

### 2. Common Issues:

#### CORS Error
- **Symptom**: "Access to fetch at ... has been blocked by CORS policy"
- **Solution**: CORS has been configured, but if you still see this:
  - Make sure you're accessing the page from `http://localhost:8000` (not `file://`)
  - Check that CORS is enabled in Azure Function App settings

#### Network Error / Failed to Fetch
- **Symptom**: "Failed to fetch" or "NetworkError"
- **Possible causes**:
  1. Internet connection issue
  2. Azure Function is down
  3. Function URL or key is incorrect
  4. Browser blocking the request

#### 401 Unauthorized
- **Symptom**: "401 Unauthorized" error
- **Solution**: Check that the function key is correct in `restaurant.html`

### 3. Test the Function Directly

You can test if the function works by running this in your terminal:

```bash
curl -X POST "https://registerrestaurantg1.azurewebsites.net/api/registerrestaurant?restaurantName=TestRestaurant&deliveryArea=Central&code=YOUR_FUNCTION_KEY"
```

If this works, the function is fine and it's a browser/CORS issue.

### 4. Verify CORS Settings

Check CORS in Azure Portal:
1. Go to Azure Portal → Function App → RegisterRestaurantG1
2. Click on "CORS" in the left menu
3. Make sure `*` or your domain is in the allowed origins

### 5. Check Function App Status

```bash
az functionapp show --name RegisterRestaurantG1 --resource-group CC_M_A_G1 --query "{state:state, defaultHostName:defaultHostName}"
```

### 6. Browser-Specific Issues

- **Chrome/Edge**: Check if extensions are blocking requests
- **Firefox**: Check privacy settings
- **Safari**: May have stricter CORS policies

### 7. Alternative: Use a Proxy

If CORS continues to be an issue, you can:
1. Deploy your frontend to GitHub Pages
2. Add your GitHub Pages URL to CORS allowed origins
3. Or use a CORS proxy (not recommended for production)

### 8. Check Function Logs

View function execution logs:
```bash
az functionapp log tail --name RegisterRestaurantG1 --resource-group CC_M_A_G1
```

Or in Azure Portal:
- Function App → Functions → RegisterRestaurant → Monitor

## Quick Fixes

1. **Hard refresh the page**: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
2. **Clear browser cache**
3. **Try a different browser**
4. **Check if you're using HTTPS vs HTTP correctly**

## Still Having Issues?

Check the browser console for the exact error message and share it for more specific help!

