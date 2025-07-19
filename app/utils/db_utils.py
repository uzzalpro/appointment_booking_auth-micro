from sqlalchemy.orm import Session

from app.db.models.models import Base


def save(db:Session,instance:Base):
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance