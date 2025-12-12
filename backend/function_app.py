import azure.functions as func
import json
import logging
import uuid
import os
from azure.data.tables import TableClient
from datetime import datetime

# Azure Functions app - all HTTP functions are defined here
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# ========================================
# RESTAURANT FUNCTIONS
# ========================================

@app.route(route="RegisterRestaurant", methods=["POST", "GET"])
def register_restaurant(req: func.HttpRequest) -> func.HttpResponse:
    """Register a new restaurant in the Restaurants table"""
    logging.info('RegisterRestaurant function triggered')

    try:
        # Accept both query params (GET) and JSON body (POST)
        restaurant_name = req.params.get("restaurantName")
        delivery_area = req.params.get("deliveryArea")

        # If not in query params, try JSON body
        if not (restaurant_name and delivery_area):
            try:
                req_body = req.get_json()
                restaurant_name = restaurant_name or req_body.get("restaurantName")
                delivery_area = delivery_area or req_body.get("deliveryArea")
            except ValueError:
                pass

        # Validation
        if not restaurant_name or not delivery_area:
            return func.HttpResponse(
                json.dumps({"error": "Both 'restaurantName' and 'deliveryArea' are required."}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

        # Get connection string
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            logging.error("AZURE_STORAGE_CONNECTION_STRING not set")
            return func.HttpResponse(
                json.dumps({"error": 'Server configuration error'}),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

        # Create table client and entity
        client = TableClient.from_connection_string(
            conn_str=connection_string,
            table_name="Restaurants"
        )

        row_key = str(uuid.uuid4())
        entity = {
            "PartitionKey": delivery_area,
            "RowKey": row_key,
            "RestaurantName": restaurant_name,
            "DeliveryArea": delivery_area
        }

        client.create_entity(entity=entity)

        return func.HttpResponse(
            json.dumps({
                "ok": True,
                "rowKey": row_key,
                "entity": entity
            }),
            status_code=201,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )


@app.route(route="RegisterMeal", methods=["POST"])
def register_meal(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('RegisterMeal function triggered')

    try:
        # get JSON body
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Request body must be valid JSON"}),
                status_code=400,
                mimetype="application/json"
            )

        restaurant_name = req_body.get('restaurantName')
        dish_name = req_body.get('dishName')
        description = req_body.get('description')
        price = req_body.get('price')
        prep_time = req_body.get('prepTime')
        area = req_body.get('area')

        # basic validation
        if not all([restaurant_name, dish_name, description, area, price, prep_time]):
            return func.HttpResponse(
                json.dumps({"error": "Missing required fields"}),
                status_code=400,
                mimetype="application/json"
            )

        price = float(price)
        prep_time = int(prep_time)

        # connection string from settings
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            logging.error("AZURE_STORAGE_CONNECTION_STRING not set")
            return func.HttpResponse(
                json.dumps({"error": 'Server configuration error'}),
                status_code=500,
                mimetype="application/json"
            )

        client = TableClient.from_connection_string(
            conn_str=connection_string,
            table_name="Meals"
        )

        entity = {
            "PartitionKey": area,
            "RowKey": str(uuid.uuid4()),
            "RestaurantName": restaurant_name,
            "DishName": dish_name,
            "Description": description,
            "Price": price,
            "PrepTime": prep_time
        }

        client.create_entity(entity=entity)

        return func.HttpResponse(
            json.dumps({
                "success": True,
                "message": "Meal registered successfully",
                "mealId": entity["RowKey"]
            }),
            status_code=200,
            mimetype="application/json"
        )

    except ValueError as e:
        logging.error(f"Validation error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Invalid data format"}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )


# ========================================
# CUSTOMER FUNCTIONS
# ========================================

@app.route(route="GetMealsByArea", methods=["GET", "POST"])
def get_meals_by_area(req: func.HttpRequest) -> func.HttpResponse:
    """Get all meals available in a specific delivery area"""
    logging.info('GetMealsByArea function triggered')

    try:
        # Get area from query params or JSON body
        area = req.params.get("area")
        
        if not area:
            try:
                req_body = req.get_json()
                area = req_body.get("area")
            except ValueError:
                pass

        if not area:
            return func.HttpResponse(
                json.dumps({"error": "Area parameter is required"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

        # Get connection string
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            logging.error("AZURE_STORAGE_CONNECTION_STRING not set")
            return func.HttpResponse(
                json.dumps({"error": 'Server configuration error'}),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

        # Query meals by area (PartitionKey)
        client = TableClient.from_connection_string(
            conn_str=connection_string,
            table_name="Meals"
        )

        # Query entities where PartitionKey equals area
        meals = []
        query_filter = f"PartitionKey eq '{area}'"
        
        for entity in client.query_entities(query_filter=query_filter):
            meal = {
                "restaurantName": entity.get("RestaurantName", ""),
                "dishName": entity.get("DishName", ""),
                "description": entity.get("Description", ""),
                "price": float(entity.get("Price", 0)),
                "prepTime": int(entity.get("PrepTime", 0)),
                "area": entity.get("PartitionKey", ""),
                "mealId": entity.get("RowKey", "")
            }
            meals.append(meal)

        return func.HttpResponse(
            json.dumps(meals),
            status_code=200,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )


@app.route(route="SubmitOrder", methods=["POST"])
def submit_order(req: func.HttpRequest) -> func.HttpResponse:
    """Submit a customer order and calculate delivery time"""
    logging.info('SubmitOrder function triggered')

    try:
        # Get JSON body
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Request body must be valid JSON"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

        customer_name = req_body.get('customerName')
        customer_address = req_body.get('customerAddress')
        customer_phone = req_body.get('customerPhone')
        delivery_area = req_body.get('deliveryArea')
        meals = req_body.get('meals', [])

        # Validation
        if not all([customer_name, customer_address, delivery_area]) or not meals:
            return func.HttpResponse(
                json.dumps({"error": "Missing required fields: customerName, customerAddress, deliveryArea, and meals"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

        # Calculate totals and delivery time
        total_price = sum(meal.get('price', 0) * meal.get('quantity', 1) for meal in meals)
        total_items = sum(meal.get('quantity', 1) for meal in meals)
        max_prep_time = max((meal.get('prepTime', 0) for meal in meals), default=0)
        estimated_delivery_time = max_prep_time + 10 + 20  # prep + pickup + delivery

        # Get connection string
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            logging.error("AZURE_STORAGE_CONNECTION_STRING not set")
            return func.HttpResponse(
                json.dumps({"error": 'Server configuration error'}),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

        # Save order to Orders table
        client = TableClient.from_connection_string(
            conn_str=connection_string,
            table_name="Orders"
        )

        order_id = str(uuid.uuid4())
        entity = {
            "PartitionKey": delivery_area,
            "RowKey": order_id,
            "CustomerName": customer_name,
            "CustomerAddress": customer_address,
            "CustomerPhone": customer_phone or "",
            "DeliveryArea": delivery_area,
            "TotalPrice": total_price,
            "TotalItems": total_items,
            "EstimatedDeliveryTime": estimated_delivery_time,
            "Status": "Pending",
            "CreatedAt": datetime.utcnow().isoformat(),
            "Meals": json.dumps(meals)  # Store meals as JSON string
        }

        client.create_entity(entity=entity)

        return func.HttpResponse(
            json.dumps({
                "success": True,
                "orderId": order_id,
                "totalPrice": total_price,
                "totalItems": total_items,
                "estimatedDeliveryTime": estimated_delivery_time,
                "message": "Order submitted successfully"
            }),
            status_code=201,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
