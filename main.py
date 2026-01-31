# Author: Dhaval Patel. Codebasics YouTube Channel

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import db_helper
import generic_helper

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

inprogress_orders = {}

@app.post("/")
async def handle_request(request: Request):
    try:
        # Retrieve the JSON data from the request
        payload = await request.json()

        # Extract the necessary information from the payload
        # based on the structure of the WebhookRequest from Dialogflow
        intent = payload['queryResult']['intent']['displayName']
        parameters = payload['queryResult']['parameters']
        output_contexts = payload['queryResult'].get('outputContexts', [])

        # Get session_id - from output_contexts or fallback to payload session
        if output_contexts:
            session_id = generic_helper.extract_session_id(output_contexts[0]["name"])
        else:
            session_id = generic_helper.extract_session_id(payload.get('session', ''))

        intent_handler_dict = {
            'order.add - context: ongoing-order': add_to_order,
            'order.remove - context: ongoing-order': remove_from_order,
            'order.complete - context: ongoing-order': complete_order,
            'order complete - context: ongoing-order': complete_order,  # Dialogflow may send with space
            'track.order - context: ongoing-tracking': track_order
        }

        handler = intent_handler_dict.get(intent)
        if handler:
            return handler(parameters, session_id)
        else:
            # Intent not handled by webhook - return fallback (Dialogflow may use its own response)
            return JSONResponse(content={
                "fulfillmentText": "How can I help you today? You can say 'New Order' or 'Track Order'."
            })
    except Exception as e:
        print(f"Error handling request: {e}")
        return JSONResponse(content={
            "fulfillmentText": "Sorry, something went wrong. Please try again. You can say 'New Order' or 'Track Order'."
        })

def save_to_db(order: dict):
    next_order_id = db_helper.get_next_order_id()

    # Insert individual items along with quantity in orders table
    for food_item, quantity in order.items():
        rcode = db_helper.insert_order_item(
            food_item,
            quantity,
            next_order_id
        )

        if rcode == -1:
            return -1

    # Now insert order tracking status
    db_helper.insert_order_tracking(next_order_id, "in progress")

    return next_order_id

def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text = "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order) 
        if order_id == -1:
            fulfillment_text = "Sorry, I couldn't process your order due to a backend error. " \
                               "Please place a new order again"
        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfillment_text = f"Awesome! Your order is placed. Here is your order Id # {order_id}. " \
                               f"Your order total is {order_total} which you can pay at the time of delivery."

        del inprogress_orders[session_id]

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def add_to_order(parameters: dict, session_id: str):
    food_items = parameters["food-item"]
    quantities = parameters["number"]

    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry I didn't understand. Can you please specify food items and quantities clearly?"
    else:
        new_food_dict = dict(zip(food_items, quantities))

        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_orders[session_id] = current_food_dict
        else:
            inprogress_orders[session_id] = new_food_dict



        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f"So far you have: {order_str}. Do you need anything else?"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText": "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
        })
    
    food_items = parameters["food-item"]
    current_order = inprogress_orders[session_id]

    removed_items = []
    no_such_items = []

    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    if len(removed_items) > 0:
        fulfillment_text = f'Removed {",".join(removed_items)} from your order!'

    if len(no_such_items) > 0:
        fulfillment_text = f' Your current order does not have {",".join(no_such_items)}'

    if len(current_order.keys()) == 0:
        fulfillment_text += " Your order is empty!"
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f" Here is what is left in your order: {order_str}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def track_order(parameters: dict, session_id: str):
    order_id = int(parameters['order_id'])
    order_status = db_helper.get_order_status(order_id)
    if order_status:
        fulfillment_text = f"The order status for order id: {order_id} is: {order_status}"
    else:
        fulfillment_text = f"No order found with order id: {order_id}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


# Simple chat endpoint for frontend (plain text in, reply out).
# For full NLP, connect Dialogflow and call its Detect Intent API here.
@app.post("/chat")
async def chat(request: Request):
    try:
        body = await request.json()
        message = (body.get("message") or "").strip()
        session_id = body.get("session_id") or ""
        if not message:
            return JSONResponse(content={"reply": "Please type a message."})
        # Placeholder reply; replace with Dialogflow Detect Intent call for full bot.
        reply = (
            "Hi! I'm the SpiceBite assistant. You can add items from the menu, or type things like "
            "'I want 2 Pav Bhaji' or 'Remove Pizza'. Connect Dialogflow to this backend for full NLP."
        )
        return JSONResponse(content={"reply": reply})
    except Exception:
        return JSONResponse(content={"reply": "Something went wrong. Please try again."})