from typing import Dict, Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

OFFER: float


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


store: Dict[int, Item] = {}


@app.get("/")
def read_rooot():
    return {"Hello to our store center, here you can store your items"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    return store.get(item_id)


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    if item.is_offer:
        item.price = calculate_new_price(item.price)
    store[item_id] = item
    return {"item_name": item.name, "item_id": item_id}


@app.put("/offer/{new_offer}")
def new_offer(new_offer: float):
    global OFFER
    OFFER = new_offer
    return {f"Offer changed to {new_offer}"}


def calculate_new_price(price: float):
    return price - price / OFFER
