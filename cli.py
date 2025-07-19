from fastapi import FastAPI
import json
from app import start_application

from app.services.message_broker_service import RabbitMQHandler
from app.services.user_info_service_executor import start_consumer

app = start_application()



if __name__ == "__main__":
    start_consumer()

