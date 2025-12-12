#!/usr/bin/env python3
"""
Milestone 2: Populate Azure Table Storage - Restaurants Table

This script populates the Restaurants table with restaurant data.
It extracts unique restaurants from the meals data structure.
"""

import os
from azure.data.tables import TableServiceClient, TableClient
from azure.core.exceptions import ResourceExistsError
import uuid

CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

if not CONNECTION_STRING:
    raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not set. Please set it in your environment.")

# Create table service client and ensure table exists
table_service_client = TableServiceClient.from_connection_string(conn_str=CONNECTION_STRING)
table_name = "Restaurants"

# Try to create table if it doesn't exist (will fail silently if it does)
try:
    table_service_client.create_table(table_name)
    print(f"✓ Table '{table_name}' created or already exists")
except ResourceExistsError:
    print(f"✓ Table '{table_name}' already exists")
except Exception as e:
    print(f"Note: {e}")

# Connect to Restaurants table
client = table_service_client.get_table_client(table_name)

# Restaurant data organized by area
# This matches the restaurants from the meals data
restaurants_data = {
    "North": [
        "Northern Bites",
        "Northside Noodles",
        "Arctic Grillhouse",
        "Northpoint Pizza Co.",
        "Golden North Curry House",
        "Polar Sushi Bar",
        "Frosty Taco Truck",
        "North Pho Kitchen",
        "Glacier Breakfast Café",
        "Northern Flame BBQ"
    ],
    "Central": [
        "Central City Grill",
        "Midtown Pasta House",
        "Central Fusion Kitchen",
        "Plaza Deli",
        "Central Sushi House",
        "Urban Tacos",
        "City Vegan Corner",
        "Central Breakfast Hub",
        "Metro Burger Joint",
        "Central Curry Kitchen"
    ],
    "South": [
        "Southern Diner",
        "Southside Grill",
        "Sunshine Sushi Bar",
        "Southside Tacos",
        "Tropical Smoothie Café",
        "Southern Pasta Bar",
        "Southside Grill & Go",
        "Flaming Wok House",
        "South Breakfast Corner",
        "Southside Pizzeria"
    ]
}

# Insert restaurants into the table
for area, restaurant_names in restaurants_data.items():
    for restaurant_name in restaurant_names:
        entity = {
            "PartitionKey": area,  # Use delivery area as PartitionKey
            "RowKey": str(uuid.uuid4()),
            "RestaurantName": restaurant_name,
            "DeliveryArea": area,
            # You can add more fields like cuisine type, rating, etc. if needed
        }
        try:
            client.create_entity(entity=entity)
            print(f"✓ Inserted: {restaurant_name} ({area})")
        except Exception as e:
            print(f"✗ Error inserting {restaurant_name}: {e}")

print("\nAll restaurants inserted successfully!")

