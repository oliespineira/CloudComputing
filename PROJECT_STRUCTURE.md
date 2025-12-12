# ByteBite - Clean Project Structure

## 📁 Directory Structure

```
CloudComputing/
│
├── backend/                    # ⭐ Azure Functions (All functions in one file)
│   ├── function_app.py        # All HTTP functions: RegisterRestaurant, RegisterMeal, GetMealsByArea, SubmitOrder
│   ├── host.json              # Azure Functions configuration
│   ├── local.settings.json     # Local development settings (connection strings)
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # 🌐 Web Frontend (HTML/CSS/JS)
│   ├── index.html             # Landing page
│   ├── restaurant.html        # Restaurant registration form
│   ├── customer.html          # Customer ordering page
│   ├── app.js                 # Frontend JavaScript (calls Azure Functions)
│   └── styles.css             # Styling
│
├── archive/                    # 📦 Old/duplicate code (for reference)
│   ├── milestone2/            # Old v1 model functions
│   └── azure_functions/       # Duplicate functions
│
└── docs/                       # 📚 Documentation
    ├── README.md
    ├── TESTING_GUIDE.md
    └── ...
```

---

## 🎯 Key Points

### ✅ All Functions in One File
**In Azure Functions v2, all HTTP functions can be in the same file!**

- **Location:** `backend/function_app.py`
- **Functions:**
  - `RegisterRestaurant` - Register a new restaurant
  - `RegisterMeal` - Register a new meal
  - `GetMealsByArea` - Get meals by delivery area
  - `SubmitOrder` - Submit customer order

**No separate directories needed!** Just use `@app.route()` decorators.

### ✅ Frontend Connected
- **Location:** `frontend/`
- **Status:** Connected to real Azure Functions
- **API Base:** `http://localhost:7071/api` (local) or your deployed URL

---

## 🚀 How to Run

### 1. Start Backend (Azure Functions)
```bash
cd backend
func start
```
Functions available at: `http://localhost:7071/api`

### 2. Start Frontend
```bash
cd frontend
python3 -m http.server 8000
```
Frontend available at: `http://localhost:8000`

---

## 📝 Function Endpoints

| Function | Method | Route | Description |
|----------|--------|-------|-------------|
| RegisterRestaurant | POST/GET | `/api/RegisterRestaurant` | Register restaurant |
| RegisterMeal | POST | `/api/RegisterMeal` | Register meal |
| GetMealsByArea | GET/POST | `/api/GetMealsByArea?area=Central` | Get meals by area |
| SubmitOrder | POST | `/api/SubmitOrder` | Submit customer order |

---

## 🔧 Configuration

### Local Development
- Backend: `backend/local.settings.json` (connection strings)
- Frontend: `frontend/app.js` (API_BASE_URL = 'http://localhost:7071/api')

### Production
- Update `API_BASE_URL` in `frontend/app.js` to your deployed function URL
- Set connection strings in Azure Portal Function App settings

---

## 📊 Azure Tables

| Table | PartitionKey | Purpose |
|-------|--------------|---------|
| Restaurants | deliveryArea | Stores restaurant info |
| Meals | area | Stores meal info |
| Orders | deliveryArea | Stores customer orders |

---

## 🧹 What Was Cleaned Up

1. ✅ **Consolidated functions** - All in `backend/function_app.py`
2. ✅ **Removed duplicates** - Archived old v1 model code
3. ✅ **Connected frontend** - Now calls real functions instead of mock data
4. ✅ **Clear structure** - Everything in logical places

---

## ❓ FAQ

**Q: Do HTTP functions need separate directories?**  
A: **No!** In v2 model, all functions go in one file with `@app.route()` decorators.

**Q: Where are the functions?**  
A: All in `backend/function_app.py` - one file, easy to find and maintain.

**Q: How do I add a new function?**  
A: Just add a new `@app.route()` function in `backend/function_app.py`.

**Q: What about the old code in milestone2/?**  
A: Archived for reference. Use `backend/` for all new work.

