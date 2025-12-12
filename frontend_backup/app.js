// ByteBite Frontend JavaScript
// This file contains shared utilities and functions

// Azure Function Configuration
// NOTE: Function keys should be stored securely (e.g., environment variables or Azure Key Vault)
// For development, get the key from Azure Portal or use: az functionapp function keys list
const AZURE_FUNCTIONS = {
    registerRestaurant: {
        url: 'https://registerrestaurantg1.azurewebsites.net/api/registerrestaurant',
        key: 'YOUR_FUNCTION_KEY_HERE' // Get from Azure Portal or Azure CLI
    },
    // Add more functions here as you create them
    // getMealsByArea: { url: '...', key: '...' },
    // registerMeal: { url: '...', key: '...' },
    // submitOrder: { url: '...', key: '...' }
};

// Utility function to call Azure Functions
async function callAzureFunction(functionName, params = {}) {
    const func = AZURE_FUNCTIONS[functionName];
    if (!func) {
        throw new Error(`Function ${functionName} not configured`);
    }
    
    const queryParams = new URLSearchParams({
        ...params,
        code: func.key
    });
    
    const url = `${func.url}?${queryParams.toString()}`;
    
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { callAzureFunction, AZURE_FUNCTIONS };
}

