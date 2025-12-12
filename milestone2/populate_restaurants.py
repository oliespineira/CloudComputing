#!/usr/bin/env python3
"""
Milestone 2: Populate Azure Table Storage with Restaurant and Meal Data

This script creates realistic restaurant and meal data for ByteBite platform.
Requirements:
- At least 3 delivery areas
- At least 10 restaurants per area
- Multiple meals per restaurant
"""

import os
import uuid
from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceExistsError

# Configuration - Update these with your Azure Storage connection string
CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")
TABLE_NAME = "Meals"  # Or use your group name as table name

# Delivery Areas
AREAS = ["Central", "North", "South"]

# Restaurant data with meals
RESTAURANT_DATA = {
    "Central": [
        {
            "name": "Pasta Paradise",
            "meals": [
                {"name": "Spaghetti Carbonara", "description": "Creamy pasta with bacon and parmesan", "prepTime": 15, "price": 12.50},
                {"name": "Margherita Pizza", "description": "Classic tomato, mozzarella, and basil", "prepTime": 20, "price": 10.00},
                {"name": "Lasagna", "description": "Layered pasta with meat sauce and cheese", "prepTime": 25, "price": 14.00},
                {"name": "Caesar Salad", "description": "Fresh romaine with caesar dressing", "prepTime": 10, "price": 8.50},
            ]
        },
        {
            "name": "Burger House",
            "meals": [
                {"name": "Classic Cheeseburger", "description": "Beef patty with cheese, lettuce, tomato", "prepTime": 12, "price": 9.50},
                {"name": "BBQ Bacon Burger", "description": "Burger with bacon and BBQ sauce", "prepTime": 15, "price": 11.00},
                {"name": "Chicken Burger", "description": "Grilled chicken breast with mayo", "prepTime": 12, "price": 10.00},
                {"name": "Sweet Potato Fries", "description": "Crispy sweet potato fries", "prepTime": 8, "price": 5.00},
            ]
        },
        {
            "name": "Sushi Express",
            "meals": [
                {"name": "Salmon Sashimi", "description": "Fresh salmon slices", "prepTime": 8, "price": 15.00},
                {"name": "California Roll", "description": "Crab, avocado, cucumber", "prepTime": 10, "price": 8.50},
                {"name": "Dragon Roll", "description": "Eel and cucumber with avocado", "prepTime": 12, "price": 13.00},
                {"name": "Miso Soup", "description": "Traditional Japanese soup", "prepTime": 5, "price": 4.00},
            ]
        },
        {
            "name": "Taco Fiesta",
            "meals": [
                {"name": "Beef Tacos (3pc)", "description": "Seasoned ground beef with lettuce and cheese", "prepTime": 10, "price": 9.00},
                {"name": "Chicken Tacos (3pc)", "description": "Grilled chicken with salsa", "prepTime": 10, "price": 9.00},
                {"name": "Vegetarian Tacos (3pc)", "description": "Black beans, corn, and avocado", "prepTime": 8, "price": 8.50},
                {"name": "Guacamole & Chips", "description": "Fresh guacamole with tortilla chips", "prepTime": 5, "price": 6.00},
            ]
        },
        {
            "name": "Curry Corner",
            "meals": [
                {"name": "Chicken Tikka Masala", "description": "Creamy tomato curry with chicken", "prepTime": 20, "price": 13.50},
                {"name": "Vegetable Biryani", "description": "Spiced rice with mixed vegetables", "prepTime": 25, "price": 11.00},
                {"name": "Butter Naan", "description": "Buttery Indian flatbread", "prepTime": 5, "price": 3.50},
                {"name": "Samosas (2pc)", "description": "Fried pastries with spiced potatoes", "prepTime": 8, "price": 5.00},
            ]
        },
        {
            "name": "Pizza Palace",
            "meals": [
                {"name": "Pepperoni Pizza", "description": "Classic pepperoni with mozzarella", "prepTime": 18, "price": 11.50},
                {"name": "Hawaiian Pizza", "description": "Ham and pineapple", "prepTime": 18, "price": 11.00},
                {"name": "Veggie Supreme", "description": "Mushrooms, peppers, onions, olives", "prepTime": 20, "price": 12.00},
                {"name": "Garlic Bread", "description": "Toasted bread with garlic butter", "prepTime": 5, "price": 4.50},
            ]
        },
        {
            "name": "Ramen House",
            "meals": [
                {"name": "Tonkotsu Ramen", "description": "Pork bone broth with chashu", "prepTime": 15, "price": 14.00},
                {"name": "Miso Ramen", "description": "Miso-based broth with vegetables", "prepTime": 12, "price": 12.50},
                {"name": "Chicken Ramen", "description": "Chicken broth with grilled chicken", "prepTime": 12, "price": 13.00},
                {"name": "Gyoza (6pc)", "description": "Pan-fried pork dumplings", "prepTime": 10, "price": 7.00},
            ]
        },
        {
            "name": "Steak & Grill",
            "meals": [
                {"name": "Ribeye Steak", "description": "8oz ribeye with sides", "prepTime": 25, "price": 22.00},
                {"name": "Grilled Chicken", "description": "Marinated chicken breast", "prepTime": 20, "price": 15.00},
                {"name": "Caesar Salad", "description": "Classic caesar with croutons", "prepTime": 8, "price": 9.00},
                {"name": "Garlic Mashed Potatoes", "description": "Creamy mashed potatoes", "prepTime": 10, "price": 6.00},
            ]
        },
        {
            "name": "Healthy Bowls",
            "meals": [
                {"name": "Chicken Quinoa Bowl", "description": "Grilled chicken, quinoa, vegetables", "prepTime": 15, "price": 12.00},
                {"name": "Salmon Poke Bowl", "description": "Fresh salmon, rice, vegetables", "prepTime": 12, "price": 14.50},
                {"name": "Veggie Power Bowl", "description": "Mixed vegetables, chickpeas, tahini", "prepTime": 10, "price": 10.50},
                {"name": "Acai Bowl", "description": "Acai, granola, fruits, honey", "prepTime": 5, "price": 8.00},
            ]
        },
        {
            "name": "Dessert Delight",
            "meals": [
                {"name": "Chocolate Lava Cake", "description": "Warm chocolate cake with ice cream", "prepTime": 12, "price": 7.50},
                {"name": "Cheesecake Slice", "description": "New York style cheesecake", "prepTime": 5, "price": 6.50},
                {"name": "Tiramisu", "description": "Classic Italian dessert", "prepTime": 5, "price": 7.00},
                {"name": "Ice Cream Sundae", "description": "Vanilla ice cream with toppings", "prepTime": 3, "price": 5.50},
            ]
        },
    ],
    "North": [
        {
            "name": "Northern Pizzeria",
            "meals": [
                {"name": "Meat Lovers Pizza", "description": "Pepperoni, sausage, ham, bacon", "prepTime": 20, "price": 13.00},
                {"name": "Margherita Pizza", "description": "Tomato, mozzarella, basil", "prepTime": 18, "price": 10.00},
                {"name": "Four Cheese Pizza", "description": "Mozzarella, cheddar, gorgonzola, parmesan", "prepTime": 18, "price": 12.00},
            ]
        },
        {
            "name": "BBQ Smokehouse",
            "meals": [
                {"name": "Pulled Pork Sandwich", "description": "Slow-cooked pork with BBQ sauce", "prepTime": 15, "price": 11.50},
                {"name": "BBQ Ribs", "description": "Full rack of ribs", "prepTime": 30, "price": 18.00},
                {"name": "Brisket Plate", "description": "Smoked brisket with sides", "prepTime": 25, "price": 16.00},
            ]
        },
        {
            "name": "Seafood Shack",
            "meals": [
                {"name": "Fish & Chips", "description": "Beer-battered fish with fries", "prepTime": 15, "price": 13.50},
                {"name": "Grilled Salmon", "description": "Atlantic salmon with vegetables", "prepTime": 18, "price": 16.00},
                {"name": "Shrimp Scampi", "description": "Garlic butter shrimp with pasta", "prepTime": 12, "price": 15.00},
            ]
        },
        {
            "name": "Wings & Things",
            "meals": [
                {"name": "Buffalo Wings (10pc)", "description": "Spicy buffalo wings", "prepTime": 15, "price": 12.00},
                {"name": "Honey BBQ Wings (10pc)", "description": "Sweet BBQ glazed wings", "prepTime": 15, "price": 12.00},
                {"name": "Loaded Nachos", "description": "Tortilla chips with cheese and toppings", "prepTime": 8, "price": 9.00},
            ]
        },
        {
            "name": "Thai Garden",
            "meals": [
                {"name": "Pad Thai", "description": "Stir-fried noodles with shrimp", "prepTime": 15, "price": 13.00},
                {"name": "Green Curry", "description": "Coconut curry with chicken", "prepTime": 18, "price": 12.50},
                {"name": "Spring Rolls (4pc)", "description": "Fresh vegetable spring rolls", "prepTime": 8, "price": 6.00},
            ]
        },
        {
            "name": "Breakfast Club",
            "meals": [
                {"name": "Full English Breakfast", "description": "Eggs, bacon, sausage, beans, toast", "prepTime": 15, "price": 11.00},
                {"name": "Avocado Toast", "description": "Sourdough with avocado and eggs", "prepTime": 8, "price": 9.50},
                {"name": "Pancake Stack", "description": "Three pancakes with syrup", "prepTime": 10, "price": 8.00},
            ]
        },
        {
            "name": "Mediterranean Bistro",
            "meals": [
                {"name": "Greek Salad", "description": "Feta, olives, tomatoes, cucumber", "prepTime": 8, "price": 10.00},
                {"name": "Lamb Gyro", "description": "Spiced lamb with tzatziki", "prepTime": 12, "price": 11.50},
                {"name": "Hummus & Pita", "description": "Creamy hummus with warm pita", "prepTime": 5, "price": 7.00},
            ]
        },
        {
            "name": "Noodle Bar",
            "meals": [
                {"name": "Beef Pho", "description": "Vietnamese noodle soup", "prepTime": 15, "price": 12.00},
                {"name": "Pad See Ew", "description": "Stir-fried wide noodles", "prepTime": 12, "price": 11.00},
                {"name": "Wonton Soup", "description": "Pork wontons in broth", "prepTime": 10, "price": 8.50},
            ]
        },
        {
            "name": "Burrito Express",
            "meals": [
                {"name": "Chicken Burrito", "description": "Grilled chicken, rice, beans, cheese", "prepTime": 10, "price": 10.00},
                {"name": "Beef Burrito", "description": "Seasoned beef with all the fixings", "prepTime": 10, "price": 10.50},
                {"name": "Veggie Burrito", "description": "Black beans, rice, vegetables", "prepTime": 8, "price": 9.50},
            ]
        },
        {
            "name": "Coffee & Pastries",
            "meals": [
                {"name": "Croissant", "description": "Buttery French croissant", "prepTime": 2, "price": 3.50},
                {"name": "Chocolate Chip Cookie", "description": "Fresh baked cookie", "prepTime": 2, "price": 2.50},
                {"name": "Blueberry Muffin", "description": "Homemade muffin", "prepTime": 2, "price": 3.00},
            ]
        },
    ],
    "South": [
        {
            "name": "Southern Fried Chicken",
            "meals": [
                {"name": "Fried Chicken (4pc)", "description": "Crispy fried chicken pieces", "prepTime": 20, "price": 12.00},
                {"name": "Chicken Sandwich", "description": "Fried chicken on brioche bun", "prepTime": 15, "price": 10.50},
                {"name": "Mac & Cheese", "description": "Creamy macaroni and cheese", "prepTime": 10, "price": 7.00},
            ]
        },
        {
            "name": "Taco Loco",
            "meals": [
                {"name": "Carnitas Tacos (3pc)", "description": "Slow-cooked pork tacos", "prepTime": 12, "price": 10.00},
                {"name": "Fish Tacos (3pc)", "description": "Battered fish with slaw", "prepTime": 12, "price": 11.00},
                {"name": "Quesadilla", "description": "Cheese quesadilla with salsa", "prepTime": 8, "price": 8.00},
            ]
        },
        {
            "name": "Soul Food Kitchen",
            "meals": [
                {"name": "Jambalaya", "description": "Spicy rice with sausage and shrimp", "prepTime": 25, "price": 14.00},
                {"name": "Gumbo", "description": "Rich stew with okra and meat", "prepTime": 30, "price": 13.50},
                {"name": "Cornbread", "description": "Sweet cornbread", "prepTime": 8, "price": 4.00},
            ]
        },
        {
            "name": "Burger Joint",
            "meals": [
                {"name": "Double Cheeseburger", "description": "Two patties with cheese", "prepTime": 15, "price": 12.00},
                {"name": "Veggie Burger", "description": "Plant-based patty", "prepTime": 12, "price": 10.00},
                {"name": "Onion Rings", "description": "Crispy battered onion rings", "prepTime": 8, "price": 5.50},
            ]
        },
        {
            "name": "Poke Paradise",
            "meals": [
                {"name": "Tuna Poke Bowl", "description": "Fresh tuna, rice, vegetables", "prepTime": 10, "price": 14.00},
                {"name": "Salmon Poke Bowl", "description": "Salmon, rice, edamame", "prepTime": 10, "price": 14.50},
                {"name": "Veggie Poke Bowl", "description": "Tofu, vegetables, rice", "prepTime": 8, "price": 11.00},
            ]
        },
        {
            "name": "Pizza Corner",
            "meals": [
                {"name": "Supreme Pizza", "description": "Pepperoni, sausage, peppers, mushrooms", "prepTime": 20, "price": 13.00},
                {"name": "White Pizza", "description": "Mozzarella, ricotta, garlic", "prepTime": 18, "price": 11.50},
                {"name": "Caesar Salad", "description": "Romaine with caesar dressing", "prepTime": 8, "price": 8.50},
            ]
        },
        {
            "name": "Wok Express",
            "meals": [
                {"name": "Kung Pao Chicken", "description": "Spicy stir-fry with peanuts", "prepTime": 15, "price": 12.50},
                {"name": "Beef Lo Mein", "description": "Noodles with beef and vegetables", "prepTime": 12, "price": 11.00},
                {"name": "Egg Rolls (2pc)", "description": "Crispy vegetable egg rolls", "prepTime": 8, "price": 5.00},
            ]
        },
        {
            "name": "Sandwich Shop",
            "meals": [
                {"name": "Club Sandwich", "description": "Turkey, ham, bacon, lettuce, tomato", "prepTime": 10, "price": 10.00},
                {"name": "Reuben Sandwich", "description": "Corned beef, sauerkraut, swiss", "prepTime": 12, "price": 11.00},
                {"name": "Caprese Sandwich", "description": "Mozzarella, tomato, basil", "prepTime": 8, "price": 9.00},
            ]
        },
        {
            "name": "Ice Cream Parlor",
            "meals": [
                {"name": "Ice Cream Cone", "description": "Two scoops of your choice", "prepTime": 2, "price": 4.50},
                {"name": "Milkshake", "description": "Thick milkshake", "prepTime": 3, "price": 5.50},
                {"name": "Ice Cream Sandwich", "description": "Ice cream between cookies", "prepTime": 2, "price": 4.00},
            ]
        },
        {
            "name": "Deli Counter",
            "meals": [
                {"name": "Pastrami Sandwich", "description": "Sliced pastrami on rye", "prepTime": 8, "price": 10.50},
                {"name": "Turkey & Swiss", "description": "Sliced turkey with swiss cheese", "prepTime": 8, "price": 9.50},
                {"name": "Potato Salad", "description": "Creamy potato salad", "prepTime": 5, "price": 5.00},
            ]
        },
    ]
}


def create_table_if_not_exists(table_service_client, table_name):
    """Create the table if it doesn't exist."""
    try:
        table_service_client.create_table(table_name)
        print(f"✓ Created table: {table_name}")
    except ResourceExistsError:
        print(f"✓ Table {table_name} already exists")


def insert_meal_entity(table_client, area, restaurant_name, meal_data):
    """Insert a meal entity into Azure Table Storage."""
    row_key = str(uuid.uuid4())
    
    entity = {
        "PartitionKey": area,  # Use delivery area as PartitionKey
        "RowKey": row_key,
        "restaurantName": restaurant_name,
        "mealName": meal_data["name"],
        "description": meal_data["description"],
        "prepTime": meal_data["prepTime"],
        "price": meal_data["price"],
    }
    
    try:
        table_client.create_entity(entity=entity)
        return True
    except Exception as e:
        print(f"  ✗ Error inserting {meal_data['name']}: {e}")
        return False


def populate_data():
    """Main function to populate Azure Table Storage with restaurant and meal data."""
    if not CONNECTION_STRING:
        print("ERROR: AZURE_STORAGE_CONNECTION_STRING environment variable not set!")
        print("Please set it using:")
        print('  export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=...;AccountKey=..."')
        return
    
    print(f"Connecting to Azure Storage...")
    print(f"Table name: {TABLE_NAME}")
    print()
    
    # Create table service client
    table_service_client = TableServiceClient.from_connection_string(conn_str=CONNECTION_STRING)
    
    # Create table if it doesn't exist
    create_table_if_not_exists(table_service_client, TABLE_NAME)
    
    # Get table client
    table_client = table_service_client.get_table_client(TABLE_NAME)
    
    # Populate data
    total_restaurants = 0
    total_meals = 0
    
    for area in AREAS:
        print(f"\n📍 Processing area: {area}")
        restaurants = RESTAURANT_DATA.get(area, [])
        
        for restaurant in restaurants:
            total_restaurants += 1
            restaurant_name = restaurant["name"]
            print(f"  🍽️  {restaurant_name}")
            
            for meal in restaurant["meals"]:
                if insert_meal_entity(table_client, area, restaurant_name, meal):
                    total_meals += 1
                    print(f"    ✓ {meal['name']} - ${meal['price']:.2f}")
    
    print(f"\n{'='*60}")
    print(f"✅ Data population complete!")
    print(f"   Areas: {len(AREAS)}")
    print(f"   Restaurants: {total_restaurants}")
    print(f"   Meals: {total_meals}")
    print(f"{'='*60}")


if __name__ == "__main__":
    populate_data()

