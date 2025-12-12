import logging
import uuid
import json
import azure.functions as func

JSON_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
}

def main(req: func.HttpRequest, entity: func.Out[str]) -> func.HttpResponse:
    logging.info("HTTP trigger received to register a meal")

    # CORS preflight (optional but handy if you call from a browser)
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

    # Accept both query-string (GET) and JSON body (POST)
    meal_name = req.params.get("mealName")
    description = req.params.get("description")
    prep_time = req.params.get("prepTime")
    price = req.params.get("price")
    delivery_area = req.params.get("deliveryArea")
    restaurant_name = req.params.get("restaurantName")

    if not (meal_name and description and prep_time and price and delivery_area and restaurant_name):
        try:
            body = req.get_json()
            meal_name = meal_name or body.get("mealName")
            description = description or body.get("description")
            prep_time = prep_time or body.get("prepTime")
            price = price or body.get("price")
            delivery_area = delivery_area or body.get("deliveryArea")
            restaurant_name = restaurant_name or body.get("restaurantName")
        except ValueError:
            pass

    if not meal_name or not description or not prep_time or not price or not delivery_area or not restaurant_name:
        return func.HttpResponse(
            json.dumps({"error": "All fields are required: mealName, description, prepTime, price, deliveryArea, restaurantName"}),
            headers=JSON_HEADERS,
            status_code=400,
        )

    # Validate numeric fields
    try:
        prep_time_int = int(prep_time)
        price_float = float(price)
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "prepTime must be an integer and price must be a number"}),
            headers=JSON_HEADERS,
            status_code=400,
        )

    row_key = str(uuid.uuid4())
    # Azure Table entity must include PartitionKey and RowKey
    entity_payload = {
        "PartitionKey": delivery_area,
        "RowKey": row_key,
        "restaurantName": restaurant_name,
        "mealName": meal_name,
        "description": description,
        "prepTime": prep_time_int,
        "price": price_float,
    }

    # Write to Table via output binding
    entity.set(json.dumps(entity_payload))

    # Return something useful to the caller
    return func.HttpResponse(
        json.dumps({"ok": True, "rowKey": row_key, "entity": entity_payload}),
        headers=JSON_HEADERS,
        status_code=201,
    )

