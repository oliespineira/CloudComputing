import azure.functions as func
import json
import logging
import uuid
import os
from azure.data.tables import TableClient
from datetime import datetime, timedelta
from azure.storage.queue import QueueClient
import hashlib


# Azure Functions app - all HTTP functions are defined here
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# ========================================
# RESTAURANT FUNCTIONS
# ========================================

@app.route(route="RegisterRestaurant", methods=["POST", "GET", "OPTIONS"])
def register_restaurant(req: func.HttpRequest) -> func.HttpResponse:
    """Register a new restaurant in the Restaurants table"""
    logging.info('RegisterRestaurant function triggered')

    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

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


@app.route(route="RegisterMeal", methods=["POST", "OPTIONS"])
def register_meal(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('RegisterMeal function triggered')

    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

    try:
        # get JSON body
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Request body must be valid JSON"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
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
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
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
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
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
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )

    except ValueError as e:
        logging.error(f"Validation error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Invalid data format"}),
            status_code=400,
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


# ========================================
# CUSTOMER FUNCTIONS
# ========================================

@app.route(route="GetMealsByArea", methods=["GET", "POST", "OPTIONS"])
def get_meals_by_area(req: func.HttpRequest) -> func.HttpResponse:
    """Get all meals available in a specific delivery area"""
    logging.info('GetMealsByArea function triggered')

    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

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


@app.route(route="SubmitOrder", methods=["POST", "OPTIONS"])
def submit_order(req: func.HttpRequest) -> func.HttpResponse:
    """Submit a customer order and calculate delivery time"""
    logging.info('SubmitOrder function triggered')

    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

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

        # Create delivery entry
        deliveries_client = TableClient.from_connection_string(
            conn_str=connection_string,
            table_name="Deliveries"
        )
        
        delivery_id = str(uuid.uuid4())
        delivery_entity = {
            "PartitionKey": delivery_area,
            "RowKey": delivery_id,
            "OrderId": order_id,
            "CustomerName": customer_name,
            "CustomerAddress": customer_address,
            "RestaurantName": meals[0].get('restaurantName') if meals else "",
            "TotalPrice": total_price,
            "EstimatedDeliveryTime": estimated_delivery_time,
            "Status": "pending",
            "DriverEmail": "",
            "CreatedAt": datetime.utcnow().isoformat()
        }
        
        deliveries_client.create_entity(entity=delivery_entity)
        
        # Send notification to queue
        send_delivery_notification(delivery_id, order_id, delivery_area)

        return func.HttpResponse(
            json.dumps({
                "success": True,
                "orderId": order_id,
                "deliveryId": delivery_id,
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


# ========================================
# DRIVER FUNCTIONS - FIXED VERSION
# ========================================

@app.route(route="CheckDeliveryQueue", methods=["POST", "OPTIONS"])
def check_delivery_queue(req: func.HttpRequest) -> func.HttpResponse:
    """
    Driver checks queue for new deliveries in their area.
    Uses long polling - waits up to 30 seconds for a message.
    """
    logging.info('CheckDeliveryQueue function triggered')

    # FIXED: Proper CORS handling
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
            },
        )

    try:
        # FIXED: Better error handling for request body
        try:
            req_body = req.get_json()
        except ValueError as e:
            logging.error(f"Invalid JSON in request: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        area = req_body.get('area')
        driver_email = req_body.get('driverEmail')
        
        # FIXED: Better validation
        if not area:
            return func.HttpResponse(
                json.dumps({"error": "Area is required"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        # FIXED: Get connection string with error handling
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            logging.error("AZURE_STORAGE_CONNECTION_STRING not configured")
            return func.HttpResponse(
                json.dumps({"error": "Server configuration error - storage not configured"}),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        # FIXED: Better queue client initialization with error handling
        try:
            queue_client = get_queue_client(area)
        except Exception as e:
            logging.error(f"Failed to create queue client: {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": f"Failed to connect to queue for area {area}"}),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        # Get up to 5 messages
        try:
            messages = queue_client.receive_messages(
                messages_per_page=5,
                visibility_timeout=30  # Hide from other drivers for 30 seconds
            )
        except Exception as e:
            logging.error(f"Failed to receive messages from queue: {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": f"Failed to check queue: {str(e)}"}),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        deliveries = []
        deliveries_client = None
        
        for msg in messages:
            try:
                message_data = json.loads(msg.content)
                
                # Get full delivery details from table
                if not deliveries_client:
                    deliveries_client = TableClient.from_connection_string(
                        conn_str=connection_string,
                        table_name="Deliveries"
                    )
                
                delivery = deliveries_client.get_entity(
                    partition_key=area,
                    row_key=message_data['deliveryId']
                )
                
                # Only include if still pending (not taken by another driver)
                if delivery.get('Status') == 'pending':
                    deliveries.append({
                        "deliveryId": delivery.get("RowKey"),
                        "orderId": delivery.get("OrderId"),
                        "customerAddress": delivery.get("CustomerAddress"),
                        "customerName": delivery.get("CustomerName"),
                        "restaurantName": delivery.get("RestaurantName"),
                        "totalPrice": float(delivery.get("TotalPrice", 0)),
                        "estimatedTime": int(delivery.get("EstimatedDeliveryTime", 0)),
                        "createdAt": delivery.get("CreatedAt"),
                        "messageId": msg.id,
                        "popReceipt": msg.pop_receipt
                    })
                else:
                    # Delivery already taken - remove from queue
                    try:
                        queue_client.delete_message(msg.id, msg.pop_receipt)
                        logging.info(f"Removed already-assigned delivery {message_data['deliveryId']} from queue")
                    except Exception as del_error:
                        logging.error(f"Error deleting stale message: {str(del_error)}")
                    
            except Exception as e:
                logging.error(f"Error processing queue message: {str(e)}")
                continue
        
        # FIXED: Always return success with CORS headers
        return func.HttpResponse(
            json.dumps({
                "deliveries": deliveries,
                "count": len(deliveries)
            }),
            status_code=200,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
        
    except Exception as e:
        logging.error(f"Unexpected error in CheckDeliveryQueue: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )


@app.route(route="AcceptDeliveryFromQueue", methods=["POST", "OPTIONS"])
def accept_delivery_from_queue(req: func.HttpRequest) -> func.HttpResponse:
    """
    Driver accepts delivery and removes it from queue.
    """
    logging.info('AcceptDeliveryFromQueue function triggered')

    # FIXED: Proper CORS handling
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
            },
        )

    try:
        # FIXED: Better error handling for request body
        try:
            req_body = req.get_json()
        except ValueError as e:
            logging.error(f"Invalid JSON in request: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        delivery_id = req_body.get('deliveryId')
        driver_email = req_body.get('driverEmail')
        area = req_body.get('area')
        message_id = req_body.get('messageId')
        pop_receipt = req_body.get('popReceipt')
        
        # FIXED: Better validation
        if not all([delivery_id, driver_email, area, message_id, pop_receipt]):
            missing = []
            if not delivery_id: missing.append('deliveryId')
            if not driver_email: missing.append('driverEmail')
            if not area: missing.append('area')
            if not message_id: missing.append('messageId')
            if not pop_receipt: missing.append('popReceipt')
            
            return func.HttpResponse(
                json.dumps({"error": f"Missing required fields: {', '.join(missing)}"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            logging.error("AZURE_STORAGE_CONNECTION_STRING not configured")
            return func.HttpResponse(
                json.dumps({"error": "Server configuration error"}),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        deliveries_client = TableClient.from_connection_string(
            conn_str=connection_string,
            table_name="Deliveries"
        )
        
        # Get delivery and check if still available
        try:
            delivery = deliveries_client.get_entity(
                partition_key=area,
                row_key=delivery_id
            )
        except Exception as e:
            logging.error(f"Delivery not found: {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": "Delivery not found"}),
                status_code=404,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        # Check if already assigned
        if delivery.get('Status') != 'pending':
            logging.warning(f"Delivery {delivery_id} already assigned to {delivery.get('DriverEmail')}")
            return func.HttpResponse(
                json.dumps({"error": "Delivery already assigned to another driver"}),
                status_code=409,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        # Update delivery
        delivery['DriverEmail'] = driver_email
        delivery['Status'] = 'assigned'
        delivery['AssignedAt'] = datetime.utcnow().isoformat()
        
        try:
            deliveries_client.update_entity(entity=delivery, mode='replace')
        except Exception as e:
            logging.error(f"Failed to update delivery: {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to update delivery"}),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        # Update order status
        orders_client = TableClient.from_connection_string(
            conn_str=connection_string,
            table_name="Orders"
        )
        
        try:
            order = orders_client.get_entity(
                partition_key=area,
                row_key=delivery.get('OrderId')
            )
            order['Status'] = 'assigned'
            order['DriverEmail'] = driver_email
            orders_client.update_entity(entity=order, mode='replace')
        except Exception as e:
            logging.error(f"Failed to update order: {str(e)}")
        
        # Remove message from queue
        try:
            queue_client = get_queue_client(area)
            queue_client.delete_message(message_id, pop_receipt)
            logging.info(f"Removed delivery {delivery_id} from queue")
        except Exception as e:
            logging.error(f"Error removing message from queue: {str(e)}")
        
        # FIXED: Always return success with CORS headers
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "message": "Delivery accepted",
                "deliveryId": delivery_id,
                "assignedAt": delivery['AssignedAt']
            }),
            status_code=200,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
        
    except Exception as e:
        logging.error(f"Unexpected error in AcceptDeliveryFromQueue: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )


# ========================================
# QUEUE HELPER FUNCTIONS
# ========================================

def get_queue_client(area: str):
    """Get queue client for specific delivery area"""
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    queue_name = f"deliveries-{area.lower()}"
    return QueueClient.from_connection_string(
        conn_str=connection_string,
        queue_name=queue_name
    )

def send_delivery_notification(delivery_id: str, order_id: str, area: str):
    """Send message to queue when new delivery is created"""
    try:
        queue_client = get_queue_client(area)
        
        message = {
            "deliveryId": delivery_id,
            "orderId": order_id,
            "area": area,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "new_delivery"
        }
        
        # Send message to queue (Base64 encoded by default)
        queue_client.send_message(json.dumps(message))
        logging.info(f"Sent delivery notification to queue: {delivery_id}")
        
    except Exception as e:
        logging.error(f"Error sending queue message: {str(e)}")

        # Don't fail the order if queue fails - delivery still created in table


# ========================================
# LOGIN FUNCTION
# ========================================

@app.route(route="login", methods=["POST", "OPTIONS"])
def login(req: func.HttpRequest) -> func.HttpResponse:
    """Authenticate user and return session token"""
    logging.info('Login function triggered')

    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

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

        email = req_body.get('email', '').strip().lower()
        password = req_body.get('password', '')
        role = req_body.get('role', '')

        # Validation
        if not all([email, password, role]):
            return func.HttpResponse(
                json.dumps({"error": "Email, password, and role are required"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

        if role not in ['customer', 'restaurant', 'driver']:
            return func.HttpResponse(
                json.dumps({"error": "Invalid role. Must be customer, restaurant, or driver"}),
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

        # Connect to Users table
        client = TableClient.from_connection_string(
            conn_str=connection_string,
            table_name="Users"
        )

        # Query for user by email and role
        query_filter = f"PartitionKey eq '{role}' and Email eq '{email}'"
        
        try:
            users = list(client.query_entities(query_filter=query_filter))
            
            if not users:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid credentials"}),
                    status_code=401,
                    mimetype="application/json",
                    headers={"Access-Control-Allow-Origin": "*"}
                )
            
            user = users[0]
            
            # Simple password comparison (NOT production-ready)
            stored_password = user.get('Password', '')
            
            if password != stored_password:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid credentials"}),
                    status_code=401,
                    mimetype="application/json",
                    headers={"Access-Control-Allow-Origin": "*"}
                )
            
            # Generate simple token
            import hashlib
            token_data = f"{email}{role}{datetime.utcnow().isoformat()}"
            token = hashlib.sha256(token_data.encode()).hexdigest()
            
            from datetime import timedelta
            expires_at = (datetime.utcnow() + timedelta(hours=24)).isoformat()
            
            return func.HttpResponse(
                json.dumps({
                    "token": token,
                    "role": role,
                    "name": user.get('Name', ''),
                    "email": email,
                    "expiresAt": expires_at
                }),
                status_code=200,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
            
        except Exception as e:
            logging.error(f"Error querying users: {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": "Database error"}),
                status_code=500,
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


@app.route(route="RegisterUser", methods=["POST", "OPTIONS"])
def register_user(req: func.HttpRequest) -> func.HttpResponse:
    """Register a new user"""
    logging.info('RegisterUser function triggered')

    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

    try:
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Request body must be valid JSON"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

        name = req_body.get('name', '').strip()
        email = req_body.get('email', '').strip().lower()
        password = req_body.get('password', '')
        role = req_body.get('role', '')

        if not all([name, email, password, role]):
            return func.HttpResponse(
                json.dumps({"error": "Name, email, password, and role are required"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

        if role not in ['customer', 'restaurant', 'driver']:
            return func.HttpResponse(
                json.dumps({"error": "Invalid role"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            return func.HttpResponse(
                json.dumps({"error": 'Server configuration error'}),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

        client = TableClient.from_connection_string(
            conn_str=connection_string,
            table_name="Users"
        )

        # Check if user exists
        query_filter = f"PartitionKey eq '{role}' and Email eq '{email}'"
        existing_users = list(client.query_entities(query_filter=query_filter))
        
        if existing_users:
            return func.HttpResponse(
                json.dumps({"error": "User already exists"}),
                status_code=409,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

        # Create user
        user_id = str(uuid.uuid4())
        entity = {
            "PartitionKey": role,
            "RowKey": user_id,
            "Name": name,
            "Email": email,
            "Password": password,
            "CreatedAt": datetime.utcnow().isoformat()
        }

        client.create_entity(entity=entity)

        return func.HttpResponse(
            json.dumps({
                "success": True,
                "message": "User registered successfully",
                "userId": user_id
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
