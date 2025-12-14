import azure.functions as func
import json
import logging
import uuid
import os
import bcrypt
import jwt
import base64
import re
from azure.core.exceptions import ResourceNotFoundError
from azure.data.tables import TableClient, TableServiceClient
from datetime import datetime, timedelta
from azure.storage.queue import QueueClient
from azure.storage.blob import BlobServiceClient
import hashlib


# Azure Functions app - all HTTP functions are defined here
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

VALID_ROLES = {"customer", "restaurant", "driver"}


def _get_storage_connection_string() -> str:
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING not set")
    return connection_string


def _get_users_table_client(connection_string: str) -> TableClient:
    service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
    try:
        service_client.create_table_if_not_exists(table_name="Users")
    except Exception as exc:
        logging.warning(f"Unable to ensure Users table exists: {exc}")
    return service_client.get_table_client(table_name="Users")


def _hash_password(raw_password: str) -> str:
    return bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(raw_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(raw_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def _generate_token(email: str, role: str, name: str) -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET not configured")

    payload = {
        "sub": email,
        "role": role,
        "name": name,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

# ========================================
# AUTH FUNCTIONS
# ========================================


@app.route(route="signup", methods=["POST", "OPTIONS"])
def signup(req: func.HttpRequest) -> func.HttpResponse:
    """Create a user account and return a JWT."""
    logging.info("signup function triggered")

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
            body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Request body must be valid JSON"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )

        name = (body.get("name") or "").strip()
        email = (body.get("email") or "").strip().lower()
        password = body.get("password") or ""
        role = (body.get("role") or "").strip().lower()
        phone = (body.get("phone") or "").strip()

        if not all([name, email, password, role]):
            return func.HttpResponse(
                json.dumps({"error": "name, email, password, and role are required"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )

        if role not in VALID_ROLES:
            return func.HttpResponse(
                json.dumps({"error": "Invalid role"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )

        connection_string = _get_storage_connection_string()
        users_client = _get_users_table_client(connection_string)

        try:
            users_client.get_entity(partition_key=role, row_key=email)
            return func.HttpResponse(
                json.dumps({"error": "Account already exists"}),
                status_code=409,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )
        except ResourceNotFoundError:
            pass

        password_hash = _hash_password(password)

        entity = {
            "PartitionKey": role,
            "RowKey": email,
            "Name": name,
            "Email": email,
            "Phone": phone,
            "Role": role,
            "PasswordHash": password_hash,
            "CreatedAt": datetime.utcnow().isoformat(),
        }

        try:
            users_client.create_entity(entity=entity)
        except Exception as exc:
            logging.error(f"Failed to create user entity: {exc}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to create account"}),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )

        try:
            token = _generate_token(email=email, role=role, name=name)
        except RuntimeError as exc:
            logging.error(f"Failed to generate token: {exc}")
            error_msg = str(exc) if "JWT_SECRET" in str(exc) else "Server configuration error: JWT_SECRET not set"
            return func.HttpResponse(
                json.dumps({"error": error_msg}),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )
        except Exception as exc:
            logging.error(f"Failed to generate token: {exc}")
            return func.HttpResponse(
                json.dumps({"error": f"Token generation failed: {str(exc)}"}),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )

        return func.HttpResponse(
            json.dumps({"token": token, "role": role, "name": name}),
            status_code=201,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
        )

    except Exception as exc:
        logging.error(f"Unexpected error in signup: {exc}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
        )


@app.route(route="login", methods=["POST", "OPTIONS"])
def login(req: func.HttpRequest) -> func.HttpResponse:
    """Validate credentials and return a JWT."""
    logging.info("login function triggered")

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
            body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Request body must be valid JSON"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )

        email = (body.get("email") or "").strip().lower()
        password = body.get("password") or ""
        role = (body.get("role") or "").strip().lower()

        if not all([email, password, role]):
            return func.HttpResponse(
                json.dumps({"error": "email, password, and role are required"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )

        if role not in VALID_ROLES:
            return func.HttpResponse(
                json.dumps({"error": "Invalid role"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )

        connection_string = _get_storage_connection_string()
        users_client = _get_users_table_client(connection_string)

        try:
            user = users_client.get_entity(partition_key=role, row_key=email)
        except ResourceNotFoundError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid credentials"}),
                status_code=401,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )
        except Exception as exc:
            logging.error(f"Failed to fetch user: {exc}")
            return func.HttpResponse(
                json.dumps({"error": "Internal server error"}),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )

        if not _verify_password(password, user.get("PasswordHash", "")):
            return func.HttpResponse(
                json.dumps({"error": "Invalid credentials"}),
                status_code=401,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )

        name = user.get("Name", "")

        try:
            token = _generate_token(email=email, role=role, name=name)
        except RuntimeError as exc:
            logging.error(f"Failed to generate token: {exc}")
            error_msg = str(exc) if "JWT_SECRET" in str(exc) else "Server configuration error: JWT_SECRET not set"
            return func.HttpResponse(
                json.dumps({"error": error_msg}),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )
        except Exception as exc:
            logging.error(f"Failed to generate token: {exc}")
            return func.HttpResponse(
                json.dumps({"error": f"Token generation failed: {str(exc)}"}),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
            )

        return func.HttpResponse(
            json.dumps({"token": token, "role": role, "name": name}),
            status_code=200,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
        )

    except Exception as exc:
        logging.error(f"Unexpected error in login: {exc}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
        )

# ========================================
# BLOB STORAGE HELPER FUNCTIONS
# ========================================

def upload_image_to_blob(base64_data: str, connection_string: str) -> str:
    """
    Upload base64 encoded image to Azure Blob Storage.
    Returns the blob URL.
    """
    try:
        # Parse base64 data URL (format: data:image/jpeg;base64,/9j/4AAQ...)
        if not base64_data.startswith('data:'):
            raise ValueError("Invalid base64 data format")
        
        # Extract mime type and base64 content
        match = re.match(r'data:image/(\w+);base64,(.+)', base64_data)
        if not match:
            raise ValueError("Invalid base64 data URL format")
        
        mime_type = match.group(1).lower()
        base64_content = match.group(2)
        
        # Validate file type
        allowed_types = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        if mime_type not in allowed_types:
            raise ValueError(f"Unsupported image type: {mime_type}. Allowed: {', '.join(allowed_types)}")
        
        # Decode base64
        image_bytes = base64.b64decode(base64_content)
        
        # Validate file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB in bytes
        if len(image_bytes) > max_size:
            raise ValueError(f"Image too large: {len(image_bytes)} bytes. Maximum size: 5MB")
        
        # Generate unique filename
        file_extension = 'jpg' if mime_type == 'jpeg' else mime_type
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Upload to blob storage
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_name = "mealimages"
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=unique_filename)
        
        # Upload blob
        content_type = f"image/{mime_type}"
        
        # Simple upload - content type can be set via blob properties if needed
        # For now, just upload - browsers can usually infer image type from extension
        blob_client.upload_blob(image_bytes, overwrite=True)
        
        # Get blob URL
        blob_url = blob_client.url
        logging.info(f"✅ Image uploaded to blob storage: {blob_url} (type: {content_type})")
        
        return blob_url
        
    except Exception as e:
        logging.error(f"❌ Error uploading image to blob storage: {str(e)}")
        raise


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

    # Optional: legacy alias if any client still calls RegisterUser
    @app.route(route="RegisterUser", methods=["POST", "OPTIONS"])
    def register_user_legacy(req: func.HttpRequest) -> func.HttpResponse:
        return signup(req)


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
        image_url = req_body.get('imageUrl')
        image_file = req_body.get('imageFile')  # Base64 encoded image

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

        # Handle image: either upload to blob storage or use provided URL
        final_image_url = ""
        if image_file:
            # Upload image to blob storage
            try:
                final_image_url = upload_image_to_blob(image_file, connection_string)
                logging.info(f"Image uploaded to blob: {final_image_url}")
            except Exception as e:
                logging.error(f"Failed to upload image: {str(e)}")
                return func.HttpResponse(
                    json.dumps({"error": f"Image upload failed: {str(e)}"}),
                    status_code=400,
                    mimetype="application/json",
                    headers={"Access-Control-Allow-Origin": "*"}
                )
        elif image_url:
            # Use provided external URL
            final_image_url = image_url.strip()
            logging.info(f"Using external image URL: {final_image_url}")

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
            "PrepTime": prep_time,
            "ImageUrl": final_image_url
        }

        client.create_entity(entity=entity)

        return func.HttpResponse(
            json.dumps({
                "success": True,
                "message": "Meal registered successfully",
                "mealId": entity["RowKey"],
                "imageUrl": final_image_url
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
            image_url = entity.get("ImageUrl", "")
            
            meal = {
                "restaurantName": entity.get("RestaurantName", ""),
                "dishName": entity.get("DishName", ""),
                "description": entity.get("Description", ""),
                "price": float(entity.get("Price", 0)),
                "prepTime": int(entity.get("PrepTime", 0)),
                "area": entity.get("PartitionKey", ""),
                "mealId": entity.get("RowKey", ""),
                "imageUrl": image_url
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
    """Submit a customer order and create delivery record"""
    logging.info('SubmitOrder function triggered')

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
        req_body = req.get_json()
        
        customer_name = req_body.get('customerName')
        customer_address = req_body.get('customerAddress')
        customer_phone = req_body.get('customerPhone')
        delivery_area = req_body.get('deliveryArea')
        meals = req_body.get('meals', [])

        if not all([customer_name, customer_address, delivery_area]) or not meals:
            return func.HttpResponse(
                json.dumps({"error": "Missing required fields"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            logging.error("AZURE_STORAGE_CONNECTION_STRING not set")
            return func.HttpResponse(
                json.dumps({"error": "Server configuration error"}),
                status_code=500,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

        # Calculate totals
        total_price = sum(meal.get('price', 0) * meal.get('quantity', 1) for meal in meals)
        max_prep_time = max((meal.get('prepTime', 0) for meal in meals), default=0)
        estimated_delivery_time = max_prep_time + 10 + 20  # prep + pickup + delivery

        # Create order
        orders_client = TableClient.from_connection_string(
            conn_str=connection_string,
            table_name="Orders"
        )

        order_id = str(uuid.uuid4())
        order_entity = {
            "PartitionKey": delivery_area,
            "RowKey": order_id,
            "CustomerName": customer_name,
            "CustomerAddress": customer_address,
            "CustomerPhone": customer_phone or "",
            "TotalPrice": total_price,
            "Status": "pending",
            "CreatedAt": datetime.utcnow().isoformat(),
            "EstimatedDeliveryTime": estimated_delivery_time
        }
        orders_client.create_entity(entity=order_entity)

        # Create delivery
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
            "RestaurantName": meals[0].get('restaurantName') if meals else "Unknown",
            "TotalPrice": total_price,
            "Status": "pending",
            "EstimatedDeliveryTime": estimated_delivery_time,
            "CreatedAt": datetime.utcnow().isoformat()
        }
        deliveries_client.create_entity(entity=delivery_entity)

        # Send notification to queue for drivers
        try:
            send_delivery_notification(
                delivery_id=delivery_id,
                order_id=order_id,
                area=delivery_area,
                restaurant_name=meals[0].get('restaurantName') if meals else "Unknown",
                customer_name=customer_name
            )
        except Exception as e:
            logging.error(f"Failed to send queue notification: {str(e)}")
            # Don't fail the order if queue notification fails

        return func.HttpResponse(
            json.dumps({
                "success": True,
                "orderId": order_id,
                "deliveryId": delivery_id,
                "estimatedDeliveryTime": estimated_delivery_time,
                "totalPrice": total_price
            }),
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


@app.route(route="UpdateDeliveryStatus", methods=["POST", "OPTIONS"])
def update_delivery_status(req: func.HttpRequest) -> func.HttpResponse:
    """Driver updates delivery status"""
    logging.info('UpdateDeliveryStatus function triggered')

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
        req_body = req.get_json()
        delivery_id = req_body.get('deliveryId')
        area = req_body.get('area')
        status = req_body.get('status')
        driver_email = req_body.get('driverEmail')
        
        valid_statuses = ['picked_up', 'in_transit', 'delivered']
        
        if not all([delivery_id, area, status, driver_email]) or status not in valid_statuses:
            return func.HttpResponse(
                json.dumps({"error": "Invalid request"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        deliveries_client = TableClient.from_connection_string(
            conn_str=connection_string,
            table_name="Deliveries"
        )
        
        delivery = deliveries_client.get_entity(partition_key=area, row_key=delivery_id)
        
        if delivery.get('DriverEmail') != driver_email:
            return func.HttpResponse(
                json.dumps({"error": "Not authorized"}),
                status_code=403,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        delivery['Status'] = status
        if status == 'picked_up':
            delivery['PickedUpAt'] = datetime.utcnow().isoformat()
        elif status == 'in_transit':
            delivery['InTransitAt'] = datetime.utcnow().isoformat()
        elif status == 'delivered':
            delivery['DeliveredAt'] = datetime.utcnow().isoformat()
        
        deliveries_client.update_entity(entity=delivery, mode='replace')
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "message": f"Status updated to {status}",
                "deliveryId": delivery_id,
                "status": status
            }),
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


@app.route(route="GetMyDeliveries", methods=["GET", "OPTIONS"])
def get_my_deliveries(req: func.HttpRequest) -> func.HttpResponse:
    """Get driver's assigned deliveries"""
    logging.info('GetMyDeliveries function triggered')

    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
            },
        )

    try:
        driver_email = req.params.get("driverEmail")
        
        if not driver_email:
            return func.HttpResponse(
                json.dumps({"error": "Driver email required"}),
                status_code=400,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        deliveries_client = TableClient.from_connection_string(
            conn_str=connection_string,
            table_name="Deliveries"
        )
        
        query_filter = f"DriverEmail eq '{driver_email}'"
        deliveries = []
        
        for entity in deliveries_client.query_entities(query_filter=query_filter):
            deliveries.append({
                "deliveryId": entity.get("RowKey"),
                "orderId": entity.get("OrderId"),
                "area": entity.get("PartitionKey"),
                "customerAddress": entity.get("CustomerAddress"),
                "customerName": entity.get("CustomerName"),
                "restaurantName": entity.get("RestaurantName"),
                "totalPrice": float(entity.get("TotalPrice", 0)),
                "status": entity.get("Status"),
                "assignedAt": entity.get("AssignedAt"),
                "pickedUpAt": entity.get("PickedUpAt"),
                "deliveredAt": entity.get("DeliveredAt")
            })
        
        deliveries.sort(key=lambda x: x.get('assignedAt', ''), reverse=True)
        
        return func.HttpResponse(
            json.dumps(deliveries),
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

def send_delivery_notification(delivery_id: str, order_id: str, area: str, restaurant_name: str, customer_name: str):
    """Send message to queue when new delivery is created"""
    try:
        queue_client = get_queue_client(area)
        
        message = {
            "deliveryId": delivery_id,
            "orderId": order_id,
            "area": area,
            "restaurantName": restaurant_name,
            "customerName": customer_name,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "new_delivery"
        }
        
        queue_client.send_message(json.dumps(message))
        logging.info(f"✅ Sent delivery notification to queue: {delivery_id}")
        
    except Exception as e:
        logging.error(f"❌ Error sending queue message: {str(e)}")
        # Don't fail the order if queue notification fails


