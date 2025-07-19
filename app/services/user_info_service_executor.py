import json
import logging
from datetime import datetime

import databases
import requests
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.config import config
from app.data.request.schemas.schema import (
                                             DyamicVariablesRequestSchema)
from app.db.models.models import (ApiRequestModel,
                                  )
from app.db.session import SessionLocal

from app.services.message_broker_service import RabbitMQHandler
from app.services.notification_service import process_and_send_notification

def process_message(ch, method, properties, body):
    ch.basic_ack(delivery_tag = method.delivery_tag)
    data = json.loads(body.decode('utf-8'))
    execute_api_request(data)


def start_consumer(queue_name):
    RabbitMQHandler().consume(queue_name, process_message)


def execute_user_info_request(executions):
    """
    Executes an API request based on the request method and saves the execution history and response.
    """
    db: Session = SessionLocal()
    try:
        print(executions)
        env_id = executions['env_id']
        collection_execution_id = executions['collection_execution_id']
        
        
        env: EnvironmentVariableModel = None
        collection: CollectionModel = None

        if(env_id):
            env = get_env_by_id(db, env_id)

        if(collection_execution_id):
            collection_start = datetime.now()
            collection_execution: CollectionExecutionHistoryModel = db.query(CollectionExecutionHistoryModel).filter(CollectionExecutionHistoryModel.id == collection_execution_id).first()
            collection = get_collection_by_id(db, collection_execution.collection_id)
        
        email_data = {
                "user_id": collection.user_id if collection else None,
                "collection_name": collection.name if collection else None,
                "environment_name": env.name if env else None,
                "run_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "report_url": f"{config.DOMAIN}/apis/reports/{collection.project_id if collection else 'no_project_id'}"
            }

        collection_execution_error = False
        
        for execution in executions['executions']:
            api_request_id = execution['api_request_id']
            execution_id = execution['execution_id']
            
            try:
                print(f'Got request id {api_request_id} and execution-id {execution_id}')

                api_request_model: ApiRequestModel  = db.query(ApiRequestModel).filter(ApiRequestModel.id == api_request_id).first()
                if(not collection):
                    collection = get_collection_by_id(db, api_request_model.collection_id)
                    email_data = {
                                    "user_id": collection.user_id if collection else None,
                                    "collection_name": collection.name if collection else None,
                                    "environment_name": env.name if env else None,
                                    "run_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "report_url": f"{config.DOMAIN}/apis/reports/{collection.project_id if collection else 'no_project_id'}"
                                }

                execution_entity: ExecutionHistoryModel = db.query(ExecutionHistoryModel).filter(ExecutionHistoryModel.id == execution_id).first()
                dynamic_vars : DyamicVariablesModel = db.query(DyamicVariablesModel).filter(DyamicVariablesModel.request_id == api_request_id).all()
                api_execution_start = datetime.now()
                print("Request url: ", api_request_model.request_url)
                print("Request method: ", api_request_model.request_method)
                print("dynamic vars: ", dynamic_vars)
                updated_api_request = replace_env_in_api_request(api_request_model, env)
                
                execution_entity.run_at = datetime.utcnow()
                print("Starting execution ...................")   
                response = None
                try:
                    print("Request url: ", updated_api_request.request_url)
                    print("Request method: ", updated_api_request.request_method)
                    # Execute the request based on the method
                    if updated_api_request.request_method == 'GET':
                        response = initiate_get_request(updated_api_request.request_url, updated_api_request.request_headers)
                    elif updated_api_request.request_method == 'POST':
                        response = initiate_post_request(
                            updated_api_request.request_url,
                            updated_api_request.request_body,
                            headers=updated_api_request.request_headers
                        )
                    
                except Exception as e: 
                    traceback.print_exc()
                    execution_entity.message = str(e)
                    execution_entity.is_successful = False
                    collection_execution_error = True

                
                execution_entity.execution_duration =int((datetime.now() - api_execution_start).microseconds / 1000)
                db.commit()

                api_request_model.is_running = False
                db.commit()
                
                if(env and response):
                    env.variables = update_env_by_dynamic_var(dynamic_vars, response, env.variables)
                    flag_modified(env, "variables")
                    db.commit()
            except Exception as e:
                traceback.print_exc()
                collection_execution_error = True
                logger.error(f"Error executing API request: {e}")
                db.rollback()
        # if(collection_execution_error):
        #     collection.is_successful = False
        #     # db.commit()
        # else:
        #     collection.is_successful = check_collection_status(db, collection.id)
        
        if(collection_execution_id):
            collection.is_running = False
            # collection_execution.is_completed = True
            if(collection_execution_error):
                collection_execution.is_successful = False
                collection.is_successful = False
            else:
                collection_execution.is_successful = True
                collection.is_successful = True
            collection_execution.execution_duration = int((datetime.now() - collection_start).microseconds / 1000)
        db.commit()

        if(collection_execution_error):
            process_and_send_notification(email_data, "failed")
            send_success_alert_email(email_data)
        else:
            process_and_send_notification(email_data, "success")
        print("collection execution completed")
    except Exception as e: 
        traceback.print_exc()  
        # send_success_alert_email(email_data)
        print("error happened") 
    finally:
        db.close()