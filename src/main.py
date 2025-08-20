import asyncio
import time
from prometheus_client.utils import INF
import psutil
import random

from typing import Any, Dict, Union

from fastapi import FastAPI, Request, Response
from pydantic import BaseModel

from prometheus_client import Counter, Histogram, Gauge, generate_latest

app = FastAPI()

# Metrics definitions
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status_code"]
)
REQUEST_DURATION = Histogram(
    "request_duration_seconds",
    "Request duration in seconds",
    [
        "path",
    ],
    buckets=[
        0.005,
        0.01,
        0.025,
        0.05,
        0.1,
        0.3,
        0.5,
        0.7,
        0.8,
        0.9,
        1.0,
        1.5,
        2.5,
        INF,
    ],
)
CPU_USAGE = Gauge("cpu_usage_percent", "CPU usage percent")
MEMORY_USAGE = Gauge("memory_usage_percent", "Memory usage percent")

OFFER: float = 5


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


raw_prices: Dict[int, float] = {}
store: Dict[int, Item] = {}


@app.middleware("http")
async def metrics_middleware(request: Request, call_next: Any):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    REQUEST_COUNT.labels(
        request.method, request.url.path, str(response.status_code)
    ).inc
    REQUEST_DURATION.labels(path=request.url.path).observe(duration)
    return response


@app.get("/")
async def read_rooot():
    return {"Hello to our store center, here you can store your items"}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return store.get(item_id)


@app.post("/items")
async def add_item(item: Item):
    id = store.__len__() + 1
    if item.is_offer:
        item.price = calculate_new_price(item.price)
    raw_prices[id] = item.price
    store[id] = item
    return {"item_name": item.name, "item_id": id}


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    if item.is_offer:
        item.price = calculate_new_price(item.price)
    store[item_id] = item
    return {"item_name": item.name, "item_id": item_id}


@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    del store[item_id]
    return {"Succes"}


@app.put("/offer/{new_offer}")
async def new_offer(new_offer: float):
    global OFFER
    OFFER = new_offer
    for id, item in store.items():
        if item.is_offer:
            item.price = calculate_new_price(raw_prices[id])

    return {f"Offer changed to {new_offer}"}


@app.patch("/items/{item_id}/{new_name}")
async def change_name(item_id: int, new_name: str):
    store[item_id].name = new_name
    return {f"Succes change to {new_name}"}


@app.patch("/item_id/{item_id}/{offer_value}")
async def switch_offer(item_id: int, offer_value: bool):
    store[item_id].is_offer = offer_value
    return {f"is offer changed to {offer_value}"}


@app.get("/offer")
async def get_offer():
    delay = random.uniform(0, 1)
    await asyncio.sleep(delay)
    return {"offer": OFFER}


@app.get("/metrics")
async def metrics():
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.virtual_memory().percent)
    return Response(generate_latest(), media_type="text/plain")


def calculate_new_price(price: float):
    return price - price / OFFER
