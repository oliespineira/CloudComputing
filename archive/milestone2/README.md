# Milestone 2: Restaurant and Meal Data Population

This milestone focuses on populating Azure Table Storage with restaurant and meal data for the ByteBite platform.

## Requirements Met

✅ **3 Delivery Areas**: North, Central, South  
✅ **10+ Restaurants per Area**: 10 restaurants in each area (30 total)  
✅ **Multiple Meals per Restaurant**: 3-5 meals per restaurant  
✅ **Data stored in Azure Table Storage**: Both `Restaurants` and `Meals` tables

## Files

### Data Population Scripts

1. **`populate_restaurants_table.py`**
   - Populates the `Restaurants` table
   - Creates restaurant entities with:
     - `PartitionKey`: Delivery area (North/Central/South)
     - `RowKey`: Unique UUID
     - `RestaurantName`: Name of the restaurant
     - `DeliveryArea`: Delivery area

2. **`populate_meals.py`**
   - Populates the `Meals` table
   - Creates meal entities with:
     - `PartitionKey`: Delivery area
     - `RowKey`: Unique UUID
     - `RestaurantName`: Name of the restaurant
     - `DishName`: Name of the dish
     - `Description`: Description of the meal
     - `Price`: Price of the meal
     - `PrepTime`: Preparation time in minutes

### Azure Functions

1. **`RegisterRestaurant/`**
   - HTTP-triggered Azure Function to register new restaurants
   - Accepts: `restaurantName`, `deliveryArea`
   - Writes to `Restaurants` table

2. **`RegisterMeal/`**
   - HTTP-triggered Azure Function to register new meals
   - Accepts: `mealName`, `description`, `prepTime`, `price`, `deliveryArea`, `restaurantName`
   - Writes to `Meals` table

## Usage

### Prerequisites

1. Set your Azure Storage connection string:
   ```bash
   export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=...;AccountKey=..."
   ```

2. Ensure the tables exist in Azure Table Storage:
   - `Restaurants`
   - `Meals`

### Running the Scripts

1. **Populate Restaurants Table:**
   ```bash
   python3 populate_restaurants_table.py
   ```

2. **Populate Meals Table:**
   ```bash
   python3 populate_meals.py
   ```

### Setting up Azure Functions

Follow the lab instructions to:
1. Initialize the Function App
2. Deploy the functions
3. Configure connection strings in `local.settings.json` and Azure Portal

## Data Structure

### Restaurants Table
- **PartitionKey**: Delivery area (North, Central, South)
- **RowKey**: UUID
- **RestaurantName**: String
- **DeliveryArea**: String

### Meals Table
- **PartitionKey**: Delivery area (North, Central, South)
- **RowKey**: UUID
- **RestaurantName**: String
- **DishName**: String
- **Description**: String
- **Price**: Number
- **PrepTime**: Number (minutes)

## Statistics

- **Total Restaurants**: 30 (10 per area)
- **Total Meals**: ~150 (varies by restaurant, typically 3-5 meals each)
- **Delivery Areas**: 3 (North, Central, South)

