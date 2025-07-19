import json
import logging
from datetime import datetime

import databases
import requests
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.config import config
from app.data.schemas.schema import (UserCreateSchema)
from app.db.models.models import (UserModel)
from app.db.session import SessionLocal

from app.services.message_broker_service import RabbitMQHandler
import json
import redis

# Initialize Redis
redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

def process_message(ch, method, properties, body):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    data = json.loads(body.decode('utf-8'))
    execute_user_info_request(data)

def start_consumer():
    queue_name = "user-info-queue"
    RabbitMQHandler().consume(queue_name, process_message)

def execute_user_info_request(message):
    try:
        print("Received message:", message)
        if message.get("event") == "user_created":
            user_data = message["data"]
            user_id = user_data["user_id"]
            # ✅ Store user data in Redis
            redis_client.set(f"user:{user_id}", json.dumps(user_data))
            print(f"Cached user:{user_id} in Redis.")
    except Exception as e:
        print("Error handling user info:", e)

        