# Azure Blob Storage for Meal Images - Setup Guide

## Overview

The ByteBite platform now supports **direct image uploads** to Azure Blob Storage in addition to external image URLs. Restaurants can either:
- **Upload an image file** directly (JPG, PNG, GIF, WebP - max 5MB)
- **Provide an external image URL** (existing functionality)

## What Was Implemented

### 1. Backend Changes (`backend/function_app.py`)

- ✅ Added `azure-storage-blob` import
- ✅ Created `upload_image_to_blob()` helper function that:
  - Validates file type (jpg, jpeg, png, gif, webp)
  - Validates file size (max 5MB)
  - Generates unique filenames using UUID
  - Uploads to `mealimages` container
  - Returns blob URL
- ✅ Updated `RegisterMeal` function to:
  - Accept both `imageUrl` (string) OR `imageFile` (base64)
  - Upload to blob storage if `imageFile` provided
  - Use external URL if `imageUrl` provided
  - Maintain backward compatibility

### 2. Frontend Changes

**`docs/restaurant.html`:**
- ✅ Added file input for image upload
- ✅ Added image preview functionality
- ✅ Clear UI showing "Option 1: Upload File" vs "Option 2: Provide URL"
- ✅ File validation (size, type) with user feedback

**`docs/app.js`:**
- ✅ File reading and base64 conversion
- ✅ Validation before submission
- ✅ Sends `imageFile` (base64) or `imageUrl` to API
- ✅ Clears preview on form reset

### 3. Dependencies

**`backend/requirements.txt`:**
- ✅ Added `azure-storage-blob`

## Deployment Steps

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Or in Azure Functions, the dependencies will be installed automatically when you deploy.

### Step 2: Verify Blob Container

The `mealimages` container should already exist. To verify or create it:

```bash
# Using Azure CLI
az storage container create \
  --name mealimages \
  --account-name cgp1storage \
  --resource-group CC_M_A_G1 \
  --public-access blob
```

**Important:** The container must have **public blob access** so customers can view images.

### Step 3: Deploy Backend

Deploy the updated `function_app.py` and `requirements.txt` to Azure Functions:

```bash
cd backend
func azure functionapp publish bytebite-functions
```

### Step 4: Verify Environment Variables

Ensure these are set in Azure Function App settings:
- ✅ `AZURE_STORAGE_CONNECTION_STRING` - Already configured
- ✅ `JWT_SECRET` - Already configured

### Step 5: Deploy Frontend

Commit and push frontend changes:

```bash
git add docs/restaurant.html docs/app.js
git commit -m "Add blob storage image upload support"
git push origin finalBranch
```

GitHub Pages will automatically update.

## Testing

### Test Scenario 1: Upload Image File

1. Go to Restaurant Portal
2. Fill in meal details
3. Click "Upload Image File"
4. Select an image (JPG, PNG, etc.)
5. See preview appear
6. Submit form
7. ✅ Image should upload to blob storage
8. ✅ Blob URL should be stored in Meals table
9. ✅ Image should appear on customer page

### Test Scenario 2: External URL

1. Go to Restaurant Portal
2. Fill in meal details
3. Enter image URL in "Option 2" field
4. Submit form
5. ✅ URL should be stored as-is (backward compatible)

### Test Scenario 3: Validation

1. Try uploading file > 5MB → Should show error
2. Try uploading non-image file → Should show error
3. Try providing both file and URL → Should show error

## API Request Examples

### Upload Image File:
```json
{
  "restaurantName": "Pizza Place",
  "dishName": "Margherita",
  "description": "Classic pizza",
  "price": 12.99,
  "prepTime": 20,
  "area": "Central",
  "imageFile": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Meal registered successfully",
  "mealId": "abc-123-def",
  "imageUrl": "https://cgp1storage.blob.core.windows.net/mealimages/abc-123-def.jpg"
}
```

### External URL:
```json
{
  "restaurantName": "Pizza Place",
  "dishName": "Margherita",
  "description": "Classic pizza",
  "price": 12.99,
  "prepTime": 20,
  "area": "Central",
  "imageUrl": "https://example.com/pizza.jpg"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Meal registered successfully",
  "mealId": "abc-123-def",
  "imageUrl": "https://example.com/pizza.jpg"
}
```

## Blob Storage Details

- **Container:** `mealimages`
- **Storage Account:** `cgp1storage`
- **Access Level:** Public Blob (readable by anyone)
- **File Naming:** `{uuid}.{extension}` (e.g., `a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg`)
- **Max File Size:** 5MB
- **Supported Formats:** JPG, JPEG, PNG, GIF, WebP

## Troubleshooting

### Images not displaying on customer page:
- ✅ Check blob container has public access
- ✅ Verify blob URL is correct in Meals table
- ✅ Check browser console for CORS errors

### Upload fails:
- ✅ Check `AZURE_STORAGE_CONNECTION_STRING` is set
- ✅ Verify `mealimages` container exists
- ✅ Check file size is under 5MB
- ✅ Verify file type is supported

### Backend errors:
- ✅ Check Azure Functions logs
- ✅ Verify `azure-storage-blob` is installed
- ✅ Check connection string permissions

## Files Modified

1. ✅ `backend/function_app.py` - Added blob upload functionality
2. ✅ `backend/requirements.txt` - Added azure-storage-blob
3. ✅ `docs/restaurant.html` - Added file input and preview
4. ✅ `docs/app.js` - Added file upload handling

## Backward Compatibility

✅ **Fully backward compatible** - Existing code using `imageUrl` will continue to work exactly as before. The new `imageFile` parameter is optional.

