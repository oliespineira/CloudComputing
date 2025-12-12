# GitHub Pages Fix

## ✅ Fixed

Copied all frontend files to `docs/` folder:
- ✅ `index.html`
- ✅ `restaurant.html`
- ✅ `customer.html`
- ✅ `styles.css`
- ✅ `app.js`

GitHub Pages serves from the `docs/` folder.

---

## ⚠️ Important: Update API URL for Production

The `docs/app.js` currently points to:
```javascript
const API_BASE_URL = 'http://localhost:7071/api';
```

**For GitHub Pages to work with Azure Functions, you need to:**

1. **Deploy your functions to Azure** (if not already done)
2. **Update `docs/app.js`** with your deployed function URL:
   ```javascript
   const API_BASE_URL = 'https://YOUR_FUNCTION_APP.azurewebsites.net/api';
   ```

3. **Commit and push** the change

---

## 🔧 GitHub Pages Configuration

Make sure GitHub Pages is configured to serve from:
- **Source:** `docs` folder
- **Branch:** `main` (or your default branch)

To check/update:
1. Go to GitHub repo → Settings → Pages
2. Source: Select "Deploy from a branch"
3. Branch: `main` / `docs` folder

---

## 📝 Next Steps

1. ✅ Files are in `docs/` folder (done)
2. ⏳ Deploy functions to Azure (if needed)
3. ⏳ Update `API_BASE_URL` in `docs/app.js` to deployed URL
4. ⏳ Make sure GitHub Pages is enabled and pointing to `docs/` folder

---

## 🧪 Test Locally

To test the docs folder locally:
```bash
cd docs
python3 -m http.server 8000
```

Open: `http://localhost:8000`

