from sqlalchemy import Boolean, Column, Integer, String, DateTime
from database import Base
import datetime


class Operator(Base):
    __tablename__ = "queue"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    in_queue = Column(Boolean, default=False)
    next = Column(Boolean, default=False)
    numTickets = Column(Integer, default = 0)

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index = True)
    date = Column(DateTime, default=datetime.datetime.now)
    assignee=Column(String, default="None")



# schemas?
