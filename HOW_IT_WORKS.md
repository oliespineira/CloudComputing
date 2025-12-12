# How Your Food Ordering Platform Works

## 🎨 Current State (Milestone 3)
```
┌─────────────────────────┐
│   Your Website          │
│   (HTML/CSS/JS)         │
│                         │
│  - Shows fake meals     │
│  - Stores nothing       │
│  - All data disappears  │
└─────────────────────────┘
```

## 🚀 Future State (Milestone 4)
```
┌─────────────────────────┐
│   Your Website          │
│   (GitHub Pages)        │
│                         │
│  User clicks "Browse"   │
└───────────┬─────────────┘
            │
            │ Internet Request
            │ "Give me meals in Central area"
            ▼
┌─────────────────────────┐
│   Azure Functions       │
│   (3 tiny programs)     │
│                         │
│  1. Get Meals           │
│  2. Add Meal            │
│  3. Place Order         │
└───────────┬─────────────┘
            │
            │ Query/Save Data
            ▼
┌─────────────────────────┐
│   Azure Table Storage   │
│   (Database)            │
│                         │
│  📋 meals table         │
│  📋 orders table        │
└─────────────────────────┘
```

## 📝 Real Example: Customer Orders Food

### Step 1: User Selects Area
```javascript
// In your website (customer.html)
User selects: "Central"
Clicks: "Browse Meals"
```

### Step 2: Website Calls Azure Function
```javascript
// JavaScript sends request:
fetch('https://yourfunctions.azure.com/api/meals?area=Central')
```

### Step 3: Azure Function Queries Storage
```python
# Python function runs:
def get_meals(area):
    # Connect to Azure Table
    # Find all meals where PartitionKey = "Central"
    # Return results
```

### Step 4: Data Flows Back
```
Azure Storage → Azure Function → Your Website → User sees meals!
```

---

## 🎯 Your Three Functions (Simple Explanations)

### Function 1: getMeals
**What it does:** "Hey Azure, give me all meals in this area"
**Input:** Area name (e.g., "Central")
**Output:** List of meals
**Like:** Searching Excel for all rows in a region

### Function 2: createMeal
**What it does:** "Hey Azure, save this new meal"
**Input:** Restaurant name, dish, price, etc.
**Output:** Success/failure message
**Like:** Adding a new row to Excel

### Function 3: createOrder
**What it does:** "Hey Azure, save this customer's order"
**Input:** Customer info, selected meals
**Output:** Order confirmation
**Like:** Recording a sale in Excel

---

## 🔧 What You Need to Do (In Order)

### Phase 1: Azure Setup (30 minutes)
1. ✅ Create Azure Storage (holds data)
2. ✅ Create two tables: "meals" and "orders"
3. ✅ Create Azure Function App (runs code)

### Phase 2: Local Development (1 hour)
4. ✅ Install tools on your Mac
5. ✅ Create 3 Python files (I'll give you the code)
6. ✅ Test locally on your computer

### Phase 3: Deployment (30 minutes)
7. ✅ Upload functions to Azure
8. ✅ Connect functions to storage
9. ✅ Enable CORS (security setting)

### Phase 4: Connect Frontend (15 minutes)
10. ✅ Change 1 line in app.js (the URL)
11. ✅ Test it works
12. ✅ Deploy to GitHub Pages

---

## 💡 Simple Analogy

Think of your project like a restaurant:

- **Frontend (website)** = The menu customers see
- **Azure Functions** = The waiter taking orders
- **Azure Storage** = The kitchen keeping track of orders

Right now, you have a pretty menu but no waiter or kitchen. 
We need to add those!

---

## 🆘 Don't Worry About...

- ❌ You don't need to be a Python expert
- ❌ You don't need to understand Azure deeply
- ❌ You don't need to write complex code

I'll provide all the code. You just need to:
1. Copy/paste
2. Run a few commands
3. Click buttons in Azure Portal

---

## 📞 Next Steps

Want me to help you with:
1. **Azure Portal setup** (creating storage and functions)?
2. **Writing the Python code** for the 3 functions?
3. **Deploying everything** to Azure?
4. **All of the above** (complete walkthrough)?

Just tell me where you want to start!
