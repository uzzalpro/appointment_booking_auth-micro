from uuid import uuid4

from celery import current_app
from celery.schedules import crontab
from redbeat import RedBeatSchedulerEntry

from app.extension import db
from models import PeriodicTaskModel


def create_scheduled_task(periodic_task):
    cron_expression = periodic_task['cron_expression']
    task_path = periodic_task['task_path']
    args = periodic_task['args']
    user = periodic_task['user']
    task_id = str(uuid4())
    cron_bit = cron_expression.split(" ")
    if len(cron_bit) != 5:
        raise ValueError("Invalid cron expression")
    cron = crontab(minute=cron_bit[0], hour=cron_bit[1],
                    day_of_week=cron_bit[4], day_of_month=cron_bit[2],
                      month_of_year=cron_bit[3])
    # Create a new entry in the RedBeatSchedulerEntry
    entry = RedBeatSchedulerEntry(name=task_id, task=task_path, schedule=cron, args=args,app=current_app)
    entry.save()
    # Create a new entry in the PeriodicTask DB
    db_periodic_task = PeriodicTaskModel(task_id=task_id, task_path=task_path, 
                                    cron_syntax=cron_expression, args=str(args),user_id=user.user_id)
    db.session.add(db_periodic_task)
    db.session.commit()
    return task_id

def delete_scheduled_task_by_id(task_id):
    db_periodic_task = None
    try:
        db_periodic_task = PeriodicTaskModel.query.filter_by(task_id=task_id).first()
        if not db_periodic_task:
            return False
        entry = RedBeatSchedulerEntry.from_key("redbeat:"+task_id,app=current_app)
        entry.delete()
    except KeyError:
        return False
    finally:
        db.session.delete(db_periodic_task)
        db.session.commit()
    return True