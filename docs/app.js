// ========================================
// GLOBAL CONFIGURATION
// ========================================

// Azure Functions endpoints
// Production URL - works on GitHub Pages and locally
const API_BASE_URL = 'https://bytebite-functions-g6gng2eahnb0f2gw.westeurope-01.azurewebsites.net/api';

const API_CONFIG = {
  baseUrl: API_BASE_URL,
  endpoints: {
    registerMeal: `${API_BASE_URL}/registermeal`,
    getMealsByArea: `${API_BASE_URL}/getmealsbyarea`,
    submitOrder: `${API_BASE_URL}/submitorder`
  }
};

// Frontend now uses real Azure Functions - no mock data needed

// ========================================
// RESTAURANT PAGE FUNCTIONALITY
// ========================================

if (document.getElementById('restaurantForm')) {
  const restaurantForm = document.getElementById('restaurantForm');
  const successMessage = document.getElementById('successMessage');
  const errorMessage = document.getElementById('errorMessage');
  const errorText = document.getElementById('errorText');

  restaurantForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Hide previous messages
    successMessage.style.display = 'none';
    errorMessage.style.display = 'none';

    // Get form data
    const formData = {
      restaurantName: document.getElementById('restaurantName').value.trim(),
      dishName: document.getElementById('dishName').value.trim(),
      description: document.getElementById('description').value.trim(),
      price: parseFloat(document.getElementById('price').value),
      prepTime: parseInt(document.getElementById('prepTime').value),
      deliveryArea: document.getElementById('deliveryArea').value
    };

    // Validation
    if (!formData.restaurantName || !formData.dishName || !formData.description || 
        !formData.deliveryArea || formData.price <= 0 || formData.prepTime <= 0) {
      errorText.textContent = 'Please fill in all required fields correctly.';
      errorMessage.style.display = 'block';
      return;
    }

    try {
      // Call Azure Function to register meal
      const response = await fetch(API_CONFIG.endpoints.registerMeal, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          restaurantName: formData.restaurantName,
          dishName: formData.dishName,
          description: formData.description,
          price: formData.price,
          prepTime: formData.prepTime,
          area: formData.deliveryArea
        })
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || 'Failed to register meal');
      }

      // Show success message
      successMessage.style.display = 'block';
      restaurantForm.reset();

      // Scroll to success message
      successMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });

      // Hide success message after 5 seconds
      setTimeout(() => {
        successMessage.style.display = 'none';
      }, 5000);

    } catch (error) {
      console.error('Error submitting meal:', error);
      errorText.textContent = error.message || 'Failed to register meal. Please try again.';
      errorMessage.style.display = 'block';
    }
  });
}

// ========================================
// CUSTOMER PAGE FUNCTIONALITY
// ========================================

if (document.getElementById('areaForm')) {
  let selectedMeals = [];
  let currentArea = '';
  let currentMeals = []; // Store fetched meals for addMeal function

  const areaForm = document.getElementById('areaForm');
  const loadingState = document.getElementById('loadingState');
  const mealsContainer = document.getElementById('mealsContainer');
  const mealsGrid = document.getElementById('mealsGrid');
  const noMealsMessage = document.getElementById('noMealsMessage');
  const orderFormContainer = document.getElementById('orderFormContainer');
  const orderForm = document.getElementById('orderForm');
  const confirmationMessage = document.getElementById('confirmationMessage');
  const errorMessage = document.getElementById('errorMessage');
  const errorText = document.getElementById('errorText');

  // Area selection handler
  areaForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const area = document.getElementById('customerArea').value;
    if (!area) return;

    currentArea = area;
    selectedMeals = [];

    // Show loading state
    loadingState.style.display = 'block';
    mealsContainer.style.display = 'none';
    orderFormContainer.style.display = 'none';
    confirmationMessage.style.display = 'none';
    errorMessage.style.display = 'none';

    try {
      // Call Azure Function to get meals by area
      const response = await fetch(`${API_CONFIG.endpoints.getMealsByArea}?area=${encodeURIComponent(area)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch meals');
      }

      const meals = await response.json();
      
      // Add placeholder image URLs for meals without images
      const mealsWithImages = meals.map(meal => ({
        ...meal,
        imageUrl: `https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400&sig=${meal.mealId}`
      }));

      currentMeals = mealsWithImages; // Store for addMeal function
      displayMeals(mealsWithImages);

    } catch (error) {
      console.error('Error fetching meals:', error);
      errorText.textContent = 'Failed to load meals. Please try again.';
      errorMessage.style.display = 'block';
      loadingState.style.display = 'none';
    }
  });

  // Display meals in grid
  function displayMeals(meals) {
    loadingState.style.display = 'none';
    mealsContainer.style.display = 'block';
    document.getElementById('selectedArea').textContent = currentArea;

    if (meals.length === 0) {
      mealsGrid.innerHTML = '';
      noMealsMessage.style.display = 'block';
      return;
    }

    noMealsMessage.style.display = 'none';
    mealsGrid.innerHTML = meals.map((meal, index) => `
      <div class="meal-card" data-meal-index="${index}">
        <img src="${meal.imageUrl}" alt="${meal.dishName}" class="meal-image" 
             onerror="this.src='https://via.placeholder.com/400x200?text=No+Image'">
        <div class="meal-content">
          <div class="meal-header">
            <h3 class="meal-name">${meal.dishName}</h3>
            <span class="meal-price">€${meal.price.toFixed(2)}</span>
          </div>
          <p class="meal-restaurant">🏪 ${meal.restaurantName}</p>
          <p class="meal-description">${meal.description}</p>
          <div class="meal-info">
            <span>⏱️ ${meal.prepTime} min</span>
            <span>📍 ${meal.area}</span>
          </div>
          <div class="meal-actions">
            <button class="btn btn-add" onclick="addMeal(${index})">Add to Order</button>
          </div>
        </div>
      </div>
    `).join('');
  }

  // Add meal to order
  window.addMeal = function(index) {
    const meal = currentMeals[index];
    if (!meal) return;
    
    const existingMeal = selectedMeals.find(m => m.dishName === meal.dishName);

    if (existingMeal) {
      existingMeal.quantity++;
    } else {
      selectedMeals.push({ ...meal, quantity: 1 });
    }

    updateOrderSummary();
  };

  // Remove meal from order
  window.removeMeal = function(dishName) {
    const mealIndex = selectedMeals.findIndex(m => m.dishName === dishName);
    if (mealIndex > -1) {
      if (selectedMeals[mealIndex].quantity > 1) {
        selectedMeals[mealIndex].quantity--;
      } else {
        selectedMeals.splice(mealIndex, 1);
      }
    }

    updateOrderSummary();
  };

  // Update order summary
  function updateOrderSummary() {
    if (selectedMeals.length === 0) {
      orderFormContainer.style.display = 'none';
      return;
    }

    orderFormContainer.style.display = 'block';

    // Update selected meals display
    const selectedMealsContainer = document.getElementById('selectedMealsContainer');
    selectedMealsContainer.innerHTML = selectedMeals.map(meal => `
      <div class="selected-meal-item">
        <div>
          <div class="selected-meal-name">${meal.dishName} x${meal.quantity}</div>
          <div class="selected-meal-details">${meal.restaurantName} • €${meal.price.toFixed(2)} each</div>
        </div>
        <button class="btn btn-remove" onclick="removeMeal('${meal.dishName}')">Remove</button>
      </div>
    `).join('');

    // Update totals
    const totalItems = selectedMeals.reduce((sum, meal) => sum + meal.quantity, 0);
    const totalPrice = selectedMeals.reduce((sum, meal) => sum + (meal.price * meal.quantity), 0);

    document.getElementById('totalItems').textContent = totalItems;
    document.getElementById('totalPrice').textContent = `€${totalPrice.toFixed(2)}`;

    // Scroll to order form
    orderFormContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // Clear order button
  document.getElementById('clearOrderBtn').addEventListener('click', () => {
    selectedMeals = [];
    updateOrderSummary();
    orderForm.reset();
  });

  // Submit order
  orderForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (selectedMeals.length === 0) {
      errorText.textContent = 'Please select at least one meal.';
      errorMessage.style.display = 'block';
      return;
    }

    const orderData = {
      customerName: document.getElementById('customerName').value.trim(),
      customerAddress: document.getElementById('customerAddress').value.trim(),
      customerPhone: document.getElementById('customerPhone').value.trim(),
      specialInstructions: document.getElementById('specialInstructions').value.trim(),
      deliveryArea: currentArea,
      meals: selectedMeals,
      totalPrice: selectedMeals.reduce((sum, meal) => sum + (meal.price * meal.quantity), 0),
      totalItems: selectedMeals.reduce((sum, meal) => sum + meal.quantity, 0)
    };

    try {
      // Call Azure Function to submit order
      const response = await fetch(API_CONFIG.endpoints.submitOrder, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          customerName: orderData.customerName,
          customerAddress: orderData.customerAddress,
          customerPhone: orderData.customerPhone,
          deliveryArea: orderData.deliveryArea,
          meals: selectedMeals.map(m => ({
            dishName: m.dishName,
            restaurantName: m.restaurantName,
            price: m.price,
            prepTime: m.prepTime,
            quantity: m.quantity
          }))
        })
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || 'Failed to submit order');
      }

      // Show confirmation with data from server
      displayConfirmation(orderData, result.estimatedDeliveryTime);

    } catch (error) {
      console.error('Error submitting order:', error);
      errorText.textContent = error.message || 'Failed to place order. Please try again.';
      errorMessage.style.display = 'block';
    }
  });

  // Display order confirmation
  function displayConfirmation(orderData, estimatedTime) {
    mealsContainer.style.display = 'none';
    orderFormContainer.style.display = 'none';
    confirmationMessage.style.display = 'block';

    document.getElementById('confirmName').textContent = orderData.customerName;
    document.getElementById('confirmTotal').textContent = `€${orderData.totalPrice.toFixed(2)}`;
    document.getElementById('confirmItems').textContent = orderData.totalItems;
    document.getElementById('confirmDeliveryTime').textContent = `${estimatedTime} minutes`;
    document.getElementById('confirmAddress').textContent = orderData.customerAddress;

    confirmationMessage.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // New order button
  document.getElementById('newOrderBtn').addEventListener('click', () => {
    selectedMeals = [];
    orderForm.reset();
    areaForm.reset();
    confirmationMessage.style.display = 'none';
    mealsContainer.style.display = 'none';
    orderFormContainer.style.display = 'none';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

// ========================================
// UTILITY FUNCTIONS
// ========================================

// Format currency
function formatCurrency(amount) {
  return `€${amount.toFixed(2)}`;
}

// Validate email
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

// Validate phone
function validatePhone(phone) {
  const re = /^[\d\s\+\-\(\)]+$/;
  return re.test(phone) && phone.replace(/\D/g, '').length >= 9;
}

console.log('ByteBite app initialized - Connected to Azure Functions');