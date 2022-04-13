from fastapi import FastAPI, Depends, Request, Form, status
import uvicorn
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    queue = db.query(models.Operator).all()
    return templates.TemplateResponse("base.html",
                                      {"request": request, "rotation": queue})

@app.post("/add")
def add(request: Request, name: str = Form(...), db: Session = Depends(get_db)):
    new_operator = models.Operator(name=name, next=False)
    db.add(new_operator)
    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@app.get("/update/{operator_id}")
def update(request: Request, operator_id: int, db: Session = Depends(get_db)):
    operator = db.query(models.Operator).filter(models.Operator.id == operator_id).first()
    operator.in_queue = not operator.in_queue

    newID = getNext(operator_id, db)
    newOperator = db.query(models.Operator).filter(models.Operator.id == newID).first()
    if (operator.next):
        newOperator.next = True
    if (not operator.in_queue):
        operator.next = False

    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)

@app.get("/next/{operator_id}")
def update(request: Request, operator_id: int, db: Session = Depends(get_db)):
    operator = db.query(models.Operator).filter(models.Operator.id == operator_id).first()
    for row in db.query(models.Operator).filter(models.Operator.id != operator_id):
        row.next = False
    operator.next = True
    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)

@app.get("/delete/{operator_id}")
def delete(request: Request, operator_id: int, db: Session = Depends(get_db)):
    operator = db.query(models.Operator).filter(models.Operator.id == operator_id).first()
    db.delete(operator)
    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)

@app.get("/assigned/{operator_id}")
def assigned(request: Request, operator_id: int, db: Session = Depends(get_db)):
    operator = db.query(models.Operator).filter(models.Operator.id == operator_id).first()
    new_ticket = models.Ticket(assignee=operator.name)
    db.add(new_ticket)
    operator.numTickets = operator.numTickets + 1
    operator.next = False
    newID = getNext(operator_id, db)
    newOperator = db.query(models.Operator).filter(models.Operator.id == newID).first()
    newOperator.next = True
    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)

def getNext(operator_id: int, db: Session):
    results = db.query(models.Operator).all()
    first_operator = results[0]
    last_operator = results[-1]
    operator = db.query(models.Operator).filter(models.Operator.id == operator_id).first()
    if(operator == last_operator):
        return first_operator.id
    else:
        newID = operator_id + 1
        return newID

if __name__ == '__main__':
    uvicorn.run(app, port=8000, host="127.0.0.1")
