import pika
import uuid
import json
import logging
import traceback
import time

from app.config import config

class RabbitMQHandler(object):

    def __init__(self):
        self.credentials = pika.PlainCredentials(config.MESSAGE_BROKER_USER, config.MESSAGE_BROKER_PASSWORD)
        self.properties = pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent)
        self.exchange_name = 'user-info'
        self.queue_name = 'user-info-queue'

        
        
    def setup(self, queue_name):
        attempt = 0
        while attempt < 5:  # Retry up to 5 times
            try:
                logging.info("Setting up RabbitMQ connection and channel")
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=config.MESSAGE_BROKER_HOST,
                        port=config.MESSAGE_BROKER_PORT,
                        credentials=self.credentials,
                        heartbeat=600,  # Adjusted heartbeat
                        blocked_connection_timeout=300  # Timeout if the connection gets blocked
                    )
                )
                print(f"listening to broker. host: {config.MESSAGE_BROKER_HOST}:{config.MESSAGE_BROKER_PORT}")
        
                self.channel = self.connection.channel()
                self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='direct')
                self.channel.queue_declare(queue=queue_name, durable=True)
                self.channel.queue_bind(exchange=self.exchange_name, queue=queue_name)
                break
            except pika.exceptions.AMQPConnectionError as e:
                logging.error(f"Connection attempt {attempt + 1} failed: {e}")
                traceback.print_exc()
                attempt += 1
                time.sleep(5)  # Wait before retrying
                if attempt == 5:
                    raise ConnectionError("Unable to connect to RabbitMQ after multiple attempts")
                
    def teardown(self):
        logging.info("Tearing down RabbitMQ connection")
        if self.connection and not self.connection.is_closed:
            self.connection.close()

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def publish(self, queue_name, message):
        try:
            self.setup(queue_name)
            self.response = None
            self.corr_id = str(uuid.uuid4())
            self.channel.basic_publish(
                    exchange=self.exchange_name,
                    routing_key=queue_name,
                    properties=self.properties,
                    body=json.dumps(message)
                )
        except Exception as e:
            logging.error(f"Error while publishing message: {e}")
            traceback.print_exc()
        finally:
            self.teardown()
    
    def consume(self, queue_name, callback):
        print("Started to consume the queue")
        
        try:
            self.setup(queue_name)
            # Use auto_ack or proper acknowledgment based on your preference
            self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)
            print('Waiting for messages. To exit press CTRL+C')
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.teardown()
            logging.info("Consumer stopped")
        except pika.exceptions.ChannelClosedByBroker as e:
            logging.error(f"Channel closed by broker: {e}")
            traceback.print_exc()
            self.teardown()
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            traceback.print_exc()
            self.teardown()
         
