#!/usr/bin/env python3
"""
Milestone 2: Populate Azure Table Storage - Meals Table

This script populates the Meals table with meal data from restaurants.
Created by team member - adapted for ByteBite project.
"""

import os
from azure.data.tables import TableClient
import uuid

CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

if not CONNECTION_STRING:
    raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not set. Please set it in your environment.")

# Connect to Meals table
client = TableClient.from_connection_string(conn_str=CONNECTION_STRING, table_name="Meals")

meals_data = {
    "North": [
        ("Northern Bites", "Grilled Chicken Wrap", "Juicy grilled chicken with veggies", 8.99, 12),
        ("Northern Bites", "Beef Shawarma Plate", "Slow-roasted beef with tahini", 12.49, 18),
        ("Northern Bites", "Falafel Bowl", "Crispy falafel with hummus", 7.99, 10),
        ("Northern Bites", "Mediterranean Salad", "Greens with feta and olives", 6.49, 8),
        ("Northern Bites", "Lentil Soup", "Warm seasoned lentils", 4.99, 9),

        ("Northside Noodles", "Chicken Pad Thai", "Stir-fried noodles with peanuts", 11.99, 15),
        ("Northside Noodles", "Veggie Stir Fry", "Mixed vegetables in soy glaze", 9.49, 10),
        ("Northside Noodles", "Beef Chow Mein", "Soft noodles with savory beef", 12.99, 14),
        ("Northside Noodles", "Spicy Ramen Bowl", "Chili broth with egg and pork", 10.99, 13),
        ("Northside Noodles", "Sesame Udon", "Udon with sesame sauce", 9.99, 11),

        ("Arctic Grillhouse", "Classic Cheeseburger", "Cheddar, onion, tomato", 10.49, 12),
        ("Arctic Grillhouse", "BBQ Bacon Burger", "Smoky BBQ and crispy bacon", 12.99, 14),
        ("Arctic Grillhouse", "Waffle Fries", "Crisp seasoned fries", 3.99, 7),
        ("Arctic Grillhouse", "Chicken Tenders", "Breaded chicken strips", 8.49, 10),
        ("Arctic Grillhouse", "Grilled Veggie Burger", "Plant-based patty", 11.49, 13),

        ("Northpoint Pizza Co.", "Pepperoni Pizza", "Pepperoni & mozzarella", 13.99, 16),
        ("Northpoint Pizza Co.", "Margherita Pizza", "Basil, tomato, mozzarella", 12.99, 18),
        ("Northpoint Pizza Co.", "BBQ Chicken Pizza", "Chicken & BBQ sauce", 14.49, 17),
        ("Northpoint Pizza Co.", "Veggie Supreme Pizza", "Peppers, olives, mushrooms", 12.49, 15),
        ("Northpoint Pizza Co.", "Garlic Breadsticks", "Warm buttery sticks", 4.99, 8),

        ("Golden North Curry House", "Butter Chicken", "Creamy tomato sauce", 13.99, 20),
        ("Golden North Curry House", "Vegetable Korma", "Mild coconut curry", 11.49, 18),
        ("Golden North Curry House", "Beef Vindaloo", "Spicy curry with potatoes", 14.99, 22),
        ("Golden North Curry House", "Garlic Naan", "Freshly baked flatbread", 2.99, 6),
        ("Golden North Curry House", "Chicken Biryani", "Spiced rice with chicken", 12.49, 19),

        ("Polar Sushi Bar", "Salmon Nigiri", "Fresh-cut salmon", 12.99, 10),
        ("Polar Sushi Bar", "Spicy Tuna Roll", "Chili tuna & cucumber", 8.99, 9),
        ("Polar Sushi Bar", "California Roll", "Crab, avocado, cucumber", 7.99, 8),
        ("Polar Sushi Bar", "Tempura Shrimp Roll", "Crispy shrimp roll", 9.99, 11),
        ("Polar Sushi Bar", "Miso Soup", "Classic soy broth", 2.99, 5),

        ("Frosty Taco Truck", "Chicken Soft Tacos", "Grilled chicken + salsa", 7.49, 8),
        ("Frosty Taco Truck", "Beef Quesadilla", "Cheese & beef blend", 8.99, 10),
        ("Frosty Taco Truck", "Loaded Nachos", "Cheese, jalapeños, beef", 9.49, 9),
        ("Frosty Taco Truck", "Fish Tacos", "Crispy cod & lime sauce", 8.49, 11),
        ("Frosty Taco Truck", "Churros", "Cinnamon sugar dessert", 3.49, 6),

        ("North Pho Kitchen", "Pho Bo", "Beef broth with noodles", 12.49, 16),
        ("North Pho Kitchen", "Pho Ga", "Chicken noodle soup", 11.99, 14),
        ("North Pho Kitchen", "Spring Rolls", "Fresh rolls with shrimp", 5.99, 7),
        ("North Pho Kitchen", "Banh Mi Chicken", "Crisp baguette sandwich", 7.99, 9),
        ("North Pho Kitchen", "Vietnamese Coffee", "Sweet iced coffee", 4.49, 5),

        ("Glacier Breakfast Café", "Pancake Stack", "Maple syrup & berries", 7.99, 10),
        ("Glacier Breakfast Café", "Omelette Trio", "Peppers, cheese, onions", 8.49, 8),
        ("Glacier Breakfast Café", "Avocado Toast", "Ciabatta + avocado", 6.99, 7),
        ("Glacier Breakfast Café", "French Toast", "Cinnamon bread toast", 7.49, 9),
        ("Glacier Breakfast Café", "Breakfast Burrito", "Eggs + sausage", 8.99, 11),

        ("Northern Flame BBQ", "Smoked Brisket Plate", "Slow-cooked brisket", 15.99, 20),
        ("Northern Flame BBQ", "Pulled Pork Sandwich", "BBQ pork on brioche", 10.99, 12),
        ("Northern Flame BBQ", "Cornbread Slice", "Sweet buttery cornbread", 3.49, 5),
        ("Northern Flame BBQ", "BBQ Wings", "House sauce wings", 9.99, 13),
        ("Northern Flame BBQ", "Mac & Cheese", "Creamy cheddar pasta", 5.99, 7)
    ],

    "Central": [
        ("Central City Grill", "Grilled Steak Plate", "Medium-rare sirloin", 15.99, 18),
        ("Central City Grill", "Chicken Caesar Wrap", "Romaine + parmesan", 8.49, 10),
        ("Central City Grill", "Loaded Fries", "Cheese + bacon bits", 6.99, 7),
        ("Central City Grill", "Club Sandwich", "Turkey + ham layers", 7.99, 9),
        ("Central City Grill", "Soup of the Day", "Rotating flavors", 4.49, 6),

        ("Midtown Pasta House", "Spaghetti Bolognese", "Meat sauce pasta", 12.49, 15),
        ("Midtown Pasta House", "Fettuccine Alfredo", "Creamy parmesan sauce", 11.99, 14),
        ("Midtown Pasta House", "Pesto Penne", "Basil pesto & tomatoes", 10.49, 12),
        ("Midtown Pasta House", "Lasagna Slice", "Layered beef lasagna", 13.49, 17),
        ("Midtown Pasta House", "Garlic Knots", "Soft and buttery", 4.49, 8),

        ("Central Fusion Kitchen", "Korean Fried Chicken", "Sweet-spicy crispy chicken", 12.49, 16),
        ("Central Fusion Kitchen", "Beef Bulgogi Bowl", "Rice + marinated beef", 13.99, 14),
        ("Central Fusion Kitchen", "Crispy Dumplings", "Pork + chive dumplings", 6.49, 9),
        ("Central Fusion Kitchen", "Thai Green Curry", "Spicy coconut curry", 11.99, 15),
        ("Central Fusion Kitchen", "Tofu Rice Bowl", "Vegetarian protein bowl", 9.49, 10),

        ("Plaza Deli", "Turkey Swiss Sandwich", "Toasted multigrain", 7.49, 7),
        ("Plaza Deli", "BLT Classic", "Bacon, lettuce, tomato", 6.99, 6),
        ("Plaza Deli", "Chicken Salad Bowl", "Greens + ranch", 7.99, 8),
        ("Plaza Deli", "Tomato Basil Soup", "Smooth creamy soup", 4.49, 6),
        ("Plaza Deli", "Ham Panini", "Warm pressed sandwich", 8.49, 9),

        ("Central Sushi House", "Rainbow Roll", "Assorted fish roll", 11.99, 12),
        ("Central Sushi House", "Dragon Roll", "Eel + avocado", 12.99, 13),
        ("Central Sushi House", "California Roll", "Crab + avocado", 7.99, 7),
        ("Central Sushi House", "Shrimp Tempura Roll", "Crispy shrimp roll", 9.99, 10),
        ("Central Sushi House", "Miso Soup", "Classic starter", 2.49, 5),

        ("Urban Tacos", "Carne Asada Tacos", "Grilled beef tacos", 8.99, 8),
        ("Urban Tacos", "Chicken Quesadilla", "Melted cheese + chicken", 7.99, 9),
        ("Urban Tacos", "Street Corn Cup", "Corn with lime + cotija", 4.99, 6),
        ("Urban Tacos", "Birria Tacos", "Slow cooked beef tacos", 10.49, 12),
        ("Urban Tacos", "Guacamole & Chips", "Freshly made dip", 3.99, 5),

        ("City Vegan Corner", "Vegan Buddha Bowl", "Quinoa + veggies", 9.99, 10),
        ("City Vegan Corner", "Plant-Based Burger", "Grilled vegan patty", 11.49, 12),
        ("City Vegan Corner", "Coconut Curry Tofu", "Mild coconut curry", 10.99, 14),
        ("City Vegan Corner", "Hummus Plate", "Pita + dips", 6.49, 8),
        ("City Vegan Corner", "Vegan Wrap", "Greens + tahini sauce", 7.99, 9),

        ("Central Breakfast Hub", "Egg & Cheese Croissant", "Buttery croissant sandwich", 5.99, 7),
        ("Central Breakfast Hub", "Morning Burrito", "Eggs + sausage wrap", 7.99, 10),
        ("Central Breakfast Hub", "Berry Yogurt Bowl", "Yogurt + fruit", 6.49, 6),
        ("Central Breakfast Hub", "Hash Browns", "Crispy potatoes", 3.49, 5),
        ("Central Breakfast Hub", "Breakfast Platter", "Eggs + bacon", 8.99, 11),

        ("Metro Burger Joint", "Classic Double Burger", "Two-patty burger", 11.49, 12),
        ("Metro Burger Joint", "BBQ Onion Burger", "BBQ + caramelized onions", 12.49, 13),
        ("Metro Burger Joint", "Cheese Fries", "Fries topped with cheese", 4.99, 7),
        ("Metro Burger Joint", "Chicken Sandwich", "Crispy chicken breast", 9.49, 10),
        ("Metro Burger Joint", "Veggie Patty Burger", "Grilled plant patty", 10.99, 11),

        ("Central Curry Kitchen", "Chicken Tikka Masala", "Creamy orange curry", 13.49, 19),
        ("Central Curry Kitchen", "Chana Masala", "Chickpea curry", 10.49, 15),
        ("Central Curry Kitchen", "Lamb Rogan Josh", "Spicy Indian lamb curry", 15.99, 22),
        ("Central Curry Kitchen", "Basmati Rice", "Fluffy long-grain rice", 2.49, 5),
        ("Central Curry Kitchen", "Paneer Butter Curry", "Creamy paneer curry", 12.49, 17),
    ],

    "South": [
        ("Southern Diner", "Fried Chicken Plate", "Crispy golden chicken", 11.99, 15),
        ("Southern Diner", "Mashed Potatoes", "Butter & herbs mash", 3.49, 6),
        ("Southern Diner", "Southern Biscuit", "Fresh baked biscuit", 2.49, 5),
        ("Southern Diner", "Chicken Sandwich", "Crispy fillet sandwich", 8.49, 9),
        ("Southern Diner", "Coleslaw Cup", "Creamy cabbage slaw", 2.99, 4),

        ("Southside Grill", "BBQ Ribs Half-Rack", "Smoky tender ribs", 16.99, 20),
        ("Southside Grill", "Steak Tips Bowl", "Grilled steak pieces", 13.49, 14),
        ("Southside Grill", "Shrimp Skewers", "Citrus-marinated shrimp", 12.49, 12),
        ("Southside Grill", "Corn on the Cob", "Butter-covered corn", 3.99, 7),
        ("Southside Grill", "House Salad", "Fresh greens bowl", 5.49, 6),

        ("Sunshine Sushi Bar", "Tuna Roll", "Fresh-cut tuna roll", 8.99, 8),
        ("Sunshine Sushi Bar", "Salmon Sashimi", "Raw salmon slices", 11.49, 9),
        ("Sunshine Sushi Bar", "Crunch Roll", "Crispy topping roll", 9.99, 10),
        ("Sunshine Sushi Bar", "Eel Avocado Roll", "Sweet eel roll", 10.49, 11),
        ("Sunshine Sushi Bar", "Seaweed Salad", "Marinated seaweed", 3.99, 5),

        ("Southside Tacos", "Chicken Tacos", "Grilled chicken tacos", 7.99, 8),
        ("Southside Tacos", "Pork Carnitas Bowl", "Slow-roasted pork bowl", 10.99, 12),
        ("Southside Tacos", "Taco Combo", "Three-taco mix", 9.99, 10),
        ("Southside Tacos", "Queso Dip", "Melted cheese dip", 4.49, 6),
        ("Southside Tacos", "Chips & Salsa", "Classic side", 3.49, 4),

        ("Tropical Smoothie Café", "Mango Smoothie", "Sweet tropical blend", 5.99, 4),
        ("Tropical Smoothie Café", "Strawberry Banana Smoothie", "Fresh fruit blend", 5.49, 5),
        ("Tropical Smoothie Café", "Acai Bowl", "Granola + berries", 8.49, 7),
        ("Tropical Smoothie Café", "Chicken Pita", "Light lunch wrap", 7.99, 9),
        ("Tropical Smoothie Café", "Protein Shake", "Vanilla whey shake", 6.99, 6),

        ("Southern Pasta Bar", "Creamy Carbonara", "Bacon + parmesan", 12.49, 14),
        ("Southern Pasta Bar", "Chicken Alfredo", "Creamy white sauce", 13.49, 15),
        ("Southern Pasta Bar", "Shrimp Scampi", "Garlic butter shrimp", 14.49, 16),
        ("Southern Pasta Bar", "Tomato Penne", "Simple red sauce pasta", 10.49, 12),
        ("Southern Pasta Bar", "Parmesan Breadsticks", "Cheesy breadsticks", 4.49, 8),

        ("Southside Grill & Go", "Chicken Gyro Wrap", "Greek-seasoned chicken", 7.49, 9),
        ("Southside Grill & Go", "Beef Gyro Plate", "Sliced beef + rice", 11.99, 13),
        ("Southside Grill & Go", "Greek Salad", "Feta + olives salad", 6.49, 7),
        ("Southside Grill & Go", "Hummus & Pita", "Creamy hummus dip", 4.49, 6),
        ("Southside Grill & Go", "Lamb Wrap", "Grilled lamb wrap", 10.99, 12),

        ("Flaming Wok House", "General Tso's Chicken", "Sweet-spicy fried chicken", 11.49, 14),
        ("Flaming Wok House", "Kung Pao Shrimp", "Chili shrimp + peanuts", 12.99, 15),
        ("Flaming Wok House", "Vegetable Lo Mein", "Wok-tossed noodles", 9.49, 12),
        ("Flaming Wok House", "Sweet & Sour Pork", "Crispy pork in sauce", 11.99, 16),
        ("Flaming Wok House", "Egg Drop Soup", "Light egg soup", 2.99, 5),

        ("South Breakfast Corner", "Waffles & Syrup", "Golden waffle", 7.49, 9),
        ("South Breakfast Corner", "Egg Platter", "Eggs + bacon combo", 8.99, 10),
        ("South Breakfast Corner", "Sausage Biscuit", "Warm breakfast sandwich", 5.49, 7),
        ("South Breakfast Corner", "Fruit Cup", "Seasonal fruit mix", 3.99, 4),
        ("South Breakfast Corner", "Cinnamon Roll", "Soft cinnamon pastry", 4.99, 8),

        ("Southside Pizzeria", "Hawaiian Pizza", "Ham + pineapple", 13.49, 17),
        ("Southside Pizzeria", "Meat Lover's Pizza", "Loaded meats", 14.99, 18),
        ("Southside Pizzeria", "White Sauce Pizza", "Ricotta + garlic", 12.49, 15),
        ("Southside Pizzeria", "Pepperoni Slice", "NY-style slice", 3.99, 7),
        ("Southside Pizzeria", "Cheesy Garlic Knots", "Garlic + cheese knots", 4.49, 8),
    ]
}

for area, meals in meals_data.items():
    for restaurant, dish, description, price, prep_time in meals:
        entity = {
            "PartitionKey": area,
            "RowKey": str(uuid.uuid4()),
            "RestaurantName": restaurant,
            "DishName": dish,
            "Description": description,
            "Price": price,
            "PrepTime": prep_time
        }
        try:
            client.create_entity(entity=entity)
            print(f"✓ Inserted: {dish} from {restaurant} ({area})")
        except Exception as e:
            print(f"✗ Error inserting {dish}: {e}")

print("\nAll meals inserted successfully!")

