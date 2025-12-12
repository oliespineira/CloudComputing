import logging
import uuid
import json
import azure.functions as func

JSON_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
}

def main(req: func.HttpRequest, entity: func.Out[str]) -> func.HttpResponse:
    logging.info("HTTP trigger received to register a restaurant")

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
    restaurant_name = req.params.get("restaurantName")
    delivery_area = req.params.get("deliveryArea")

    if not (restaurant_name and delivery_area):
        try:
            body = req.get_json()
            restaurant_name = restaurant_name or body.get("restaurantName")
            delivery_area = delivery_area or body.get("deliveryArea")
        except ValueError:
            pass

    if not restaurant_name or not delivery_area:
        return func.HttpResponse(
            json.dumps({"error": "Both 'restaurantName' and 'deliveryArea' are required."}),
            headers=JSON_HEADERS,
            status_code=400,
        )

    row_key = str(uuid.uuid4())
    # Azure Table entity must include PartitionKey and RowKey
    entity_payload = {
        "PartitionKey": delivery_area,
        "RowKey": row_key,
        "RestaurantName": restaurant_name,
        "DeliveryArea": delivery_area,
    }

    # Write to Table via output binding
    entity.set(json.dumps(entity_payload))

    # Return something useful to the caller
    return func.HttpResponse(
        json.dumps({"ok": True, "rowKey": row_key, "entity": entity_payload}),
        headers=JSON_HEADERS,
        status_code=201,
    )
