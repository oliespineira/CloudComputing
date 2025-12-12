# Frontend Connection Status

## ✅ All Functions Connected

The frontend is now fully connected to Azure Functions.

### Restaurant Portal (`restaurant.html`)
- **Form ID:** `restaurantForm` ✅
- **Function:** `RegisterMeal` ✅
- **Endpoint:** `POST /api/RegisterMeal` ✅
- **Status:** Connected and working

### Customer Portal (`customer.html`)
- **Area Selection:** `areaForm` → `GetMealsByArea` ✅
- **Order Submission:** `orderForm` → `SubmitOrder` ✅
- **Endpoints:**
  - `GET /api/GetMealsByArea?area=Central` ✅
  - `POST /api/SubmitOrder` ✅
- **Status:** Connected and working

---

## 🔧 Configuration

**API Base URL:** `http://localhost:7071/api` (local development)

To change for production, update in `frontend/app.js`:
```javascript
const API_BASE_URL = 'YOUR_DEPLOYED_FUNCTION_URL/api';
```

---

## 📝 How It Works

1. **Restaurant registers meal:**
   - User fills form → Submits → Calls `RegisterMeal` → Saves to Azure Table Storage

2. **Customer browses meals:**
   - Selects area → Calls `GetMealsByArea` → Displays meals from Azure

3. **Customer places order:**
   - Selects meals → Fills order form → Calls `SubmitOrder` → Saves order to Azure

---

## 🧪 Testing

1. Start backend: `cd backend && func start`
2. Start frontend: `cd frontend && python3 -m http.server 8000`
3. Open: `http://localhost:8000`

All functions are connected and ready to use! 🎉

