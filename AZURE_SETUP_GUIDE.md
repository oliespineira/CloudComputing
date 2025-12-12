# Azure Setup Guide for Beginners

## Part 1: Create Azure Storage Account

1. Go to Azure Portal: https://portal.azure.com
2. Click "Create a resource"
3. Search for "Storage account" and click Create
4. Fill in:
   - Resource Group: Create new → "CloudComputingRG"
   - Storage account name: "foodhubstorage[yourname]" (must be unique)
   - Region: Choose closest to you
   - Performance: Standard
   - Redundancy: LRS (cheapest)
5. Click "Review + Create" → "Create"
6. Wait for deployment (1-2 minutes)

## Part 2: Create Tables

1. In your storage account, go to "Tables" (left sidebar)
2. Click "+ Table" and create:
   - Table 1: "meals"
   - Table 2: "orders"

## Part 3: Get Your Connection String

1. In storage account, go to "Access keys" (left sidebar)
2. Click "Show" next to "Connection string"
3. Copy it - you'll need this later
4. Keep it SECRET (like a password)

## Part 4: Add Sample Data (Optional for Testing)

You can manually add data through Azure Portal:
1. Go to Tables → meals
2. Click "Add entity"
3. Fill in:
   - PartitionKey: "Central"
   - RowKey: "meal-001"
   - Add properties: restaurantName, dishName, description, price, prepTime, imageUrl

---

## Part 5: Create Azure Function App

1. In Azure Portal, click "Create a resource"
2. Search for "Function App" and click Create
3. Fill in:
   - Resource Group: Use existing "CloudComputingRG"
   - Function App name: "foodhub-functions-[yourname]"
   - Runtime stack: Python 3.11
   - Region: Same as storage account
   - Operating System: Linux
   - Hosting: Consumption (Serverless)
4. Click "Review + Create" → "Create"
5. Wait for deployment

## Part 6: Install Azure Functions Core Tools (Local Development)

Run these commands in your terminal:

### macOS (using Homebrew):
```bash
brew tap azure/functions
brew install azure-functions-core-tools@4
```

### Verify installation:
```bash
func --version
```

## Part 7: Create Your Functions Project

```bash
cd /Users/inventure71/VSProjects/School/CloudComputing
mkdir backend
cd backend
func init . --python
```

This creates the structure for your Azure Functions.

---

# Next Steps

After completing the above, you'll:
1. Write 3 simple Python functions (I'll provide the code)
2. Connect them to your storage account
3. Deploy them to Azure
4. Update your website to use them

Don't worry - I'll guide you through each step!
