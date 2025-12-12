# Troubleshooting Connection Issues

## ✅ Fixed: CORS Headers Added

All functions now have CORS headers on all responses, including:
- Success responses
- Error responses  
- OPTIONS preflight requests

---

## 🔍 Common Issues & Solutions

### Issue 1: "Failed to fetch" or CORS errors

**Symptoms:**
- Browser console shows CORS errors
- Network tab shows OPTIONS request failing

**Solution:**
✅ CORS headers are now added to all functions. Restart your backend:
```bash
# Stop the current func start (Ctrl+C)
cd backend
func start
```

---

### Issue 2: Functions not running

**Check if functions are running:**
```bash
ps aux | grep "func start"
```

**Start functions:**
```bash
cd backend
func start
```

You should see:
```
Functions:
        RegisterRestaurant: [POST,GET,OPTIONS] http://localhost:7071/api/RegisterRestaurant
        RegisterMeal: [POST,OPTIONS] http://localhost:7071/api/RegisterMeal
        GetMealsByArea: [GET,POST,OPTIONS] http://localhost:7071/api/GetMealsByArea
        SubmitOrder: [POST,OPTIONS] http://localhost:7071/api/SubmitOrder
```

---

### Issue 3: Connection string not set

**Check:**
```bash
cd backend
cat local.settings.json | grep AZURE_STORAGE_CONNECTION_STRING
```

**Should have:**
```json
"AZURE_STORAGE_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=..."
```

---

### Issue 4: Frontend can't reach backend

**Check API URL in frontend:**
- Open browser console (F12)
- Check Network tab when submitting form
- Verify requests are going to `http://localhost:7071/api/...`

**Update if needed in `frontend/app.js`:**
```javascript
const API_BASE_URL = 'http://localhost:7071/api';
```

---

### Issue 5: Tables don't exist in Azure

**Create tables:**
1. Go to Azure Portal → Storage Account (`cgp1storage`)
2. Click "Tables" → "Create table"
3. Create: `Meals`, `Restaurants`, `Orders`

---

## 🧪 Test Connection

### 1. Test backend is running:
```bash
curl http://localhost:7071/api/GetMealsByArea?area=Central
```

Should return: `[]` (empty array) or list of meals

### 2. Test from browser console:
```javascript
fetch('http://localhost:7071/api/GetMealsByArea?area=Central')
  .then(r => r.json())
  .then(data => console.log('Success:', data))
  .catch(err => console.error('Error:', err));
```

### 3. Test full flow:
1. Start backend: `cd backend && func start`
2. Start frontend: `cd frontend && python3 -m http.server 8000`
3. Open: `http://localhost:8000`
4. Open browser console (F12) to see any errors

---

## 📝 Check Browser Console

**Open browser console (F12) and look for:**
- ✅ Success: Network requests show 200 status
- ❌ Error: CORS errors, 404, 500, etc.

**Common errors:**
- `CORS policy`: Backend not running or CORS headers missing
- `Failed to fetch`: Backend not accessible
- `404 Not Found`: Wrong URL or function not deployed
- `500 Internal Server Error`: Check backend logs

---

## 🔧 Quick Fixes

1. **Restart backend:**
   ```bash
   # Kill existing process
   pkill -f "func start"
   # Start fresh
   cd backend && func start
   ```

2. **Clear browser cache:**
   - Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

3. **Check both are running:**
   - Backend: `http://localhost:7071` should respond
   - Frontend: `http://localhost:8000` should show page

---

## ✅ Verification Checklist

- [ ] Backend running (`func start` shows functions)
- [ ] Frontend running (`python3 -m http.server 8000`)
- [ ] Connection string set in `local.settings.json`
- [ ] Tables exist in Azure (`Meals`, `Restaurants`, `Orders`)
- [ ] Browser console shows no CORS errors
- [ ] Network tab shows successful requests

