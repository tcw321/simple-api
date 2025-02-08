from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, init_db, Base
from models import Item
from pydantic import BaseModel
import os

app = FastAPI()

# Initialize database tables at startup, but skip during testing
@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    if not os.getenv("TESTING"):
        engine = init_db()
        Base.metadata.create_all(bind=engine)

class ItemBase(BaseModel):
    name: str

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int

    class Config:
        orm_mode = True

@app.post("/items/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item"""
    db_item = Item(name=item.name)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/{item_id}", response_model=ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    """Get an item by ID"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
