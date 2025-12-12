import azure.functions as func
import json
import logging
import uuid
import os
from azure.data.tables import TableClient

# keep this: it's the app object Azure uses
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

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
