// ========================================
// GLOBAL CONFIGURATION
// ========================================

// Azure Functions endpoints (to be updated in Milestone 4)
const API_CONFIG = {
  baseUrl: '', // Will be set when Azure Functions are deployed
  endpoints: {
    getMeals: '/api/meals',
    createMeal: '/api/meals/create',
    createOrder: '/api/orders/create'
  }
};

// Mock data for Milestone 3 (static frontend demonstration)
const MOCK_MEALS = [
  {
    restaurantName: "Mario's Pizza House",
    dishName: "Margherita Pizza",
    description: "Classic Italian pizza with fresh mozzarella, tomato sauce, and basil",
    price: 12.99,
    prepTime: 25,
    area: "Central",
    imageUrl: "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400"
  },
  {
    restaurantName: "Mario's Pizza House",
    dishName: "Pepperoni Pizza",
    description: "Loaded with premium pepperoni and mozzarella cheese",
    price: 14.99,
    prepTime: 25,
    area: "Central",
    imageUrl: "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400"
  },
  {
    restaurantName: "Sushi Zen",
    dishName: "California Roll",
    description: "Fresh crab, avocado, and cucumber wrapped in sushi rice",
    price: 11.50,
    prepTime: 15,
    area: "Central",
    imageUrl: "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=400"
  },
  {
    restaurantName: "Burger Kingdom",
    dishName: "Classic Cheeseburger",
    description: "Juicy beef patty with cheddar, lettuce, tomato, and special sauce",
    price: 9.99,
    prepTime: 20,
    area: "North",
    imageUrl: "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400"
  },
  {
    restaurantName: "Burger Kingdom",
    dishName: "Bacon Deluxe",
    description: "Double patty with crispy bacon, cheese, and BBQ sauce",
    price: 13.99,
    prepTime: 22,
    area: "North",
    imageUrl: "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=400"
  },
  {
    restaurantName: "Taco Fiesta",
    dishName: "Chicken Tacos",
    description: "Three soft tacos with grilled chicken, salsa, and guacamole",
    price: 10.50,
    prepTime: 18,
    area: "South",
    imageUrl: "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=400"
  },
  {
    restaurantName: "Pasta Paradise",
    dishName: "Carbonara",
    description: "Creamy pasta with bacon, egg, and parmesan cheese",
    price: 13.50,
    prepTime: 20,
    area: "East",
    imageUrl: "https://images.unsplash.com/photo-1612874742237-6526221588e3?w=400"
  },
  {
    restaurantName: "Asian Wok",
    dishName: "Pad Thai",
    description: "Stir-fried rice noodles with shrimp, peanuts, and vegetables",
    price: 12.00,
    prepTime: 25,
    area: "West",
    imageUrl: "https://images.unsplash.com/photo-1559314809-0d155014e29e?w=400"
  }
];

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
      deliveryArea: document.getElementById('deliveryArea').value,
      imageUrl: document.getElementById('imageUrl').value.trim()
    };

    // Validation
    if (!formData.restaurantName || !formData.dishName || !formData.description || 
        !formData.deliveryArea || formData.price <= 0 || formData.prepTime <= 0) {
      errorText.textContent = 'Please fill in all required fields correctly.';
      errorMessage.style.display = 'block';
      return;
    }

    try {
      // In Milestone 3, we simulate success
      // In Milestone 4, this will call Azure Functions
      console.log('Meal data to be submitted:', formData);

      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 500));

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
      errorText.textContent = 'Failed to register meal. Please try again.';
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
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 800));

      // In Milestone 3, use mock data
      // In Milestone 4, this will call Azure Functions
      const meals = MOCK_MEALS.filter(meal => meal.area === area);

      displayMeals(meals);

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
    const meal = MOCK_MEALS.filter(m => m.area === currentArea)[index];
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
      // In Milestone 3, simulate order submission
      // In Milestone 4, this will call Azure Functions
      console.log('Order data to be submitted:', orderData);

      // Calculate estimated delivery time
      const maxPrepTime = Math.max(...selectedMeals.map(m => m.prepTime));
      const estimatedTime = maxPrepTime + 10 + 15; // prep + pickup + delivery

      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Show confirmation
      displayConfirmation(orderData, estimatedTime);

    } catch (error) {
      console.error('Error submitting order:', error);
      errorText.textContent = 'Failed to place order. Please try again.';
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

console.log('FoodHub app initialized - Milestone 3');