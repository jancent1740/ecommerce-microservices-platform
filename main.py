from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

# Import our modules
import models
import schemas
import crud
from database import SessionLocal, engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

# FastAPI App
app = FastAPI(
    title="E-commerce API",
    description="A comprehensive e-commerce REST API with modular architecture",
    version="1.0.0"
)

# ITEM ENDPOINTS
@app.get("/items", response_model=List[schemas.ItemResponse], tags=["Items"])
def get_all_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all items in the inventory"""
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@app.post("/items", response_model=schemas.ItemResponse, tags=["Items"])
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """Create a new item"""
    return crud.create_item(db=db, item=item)

@app.get("/items/{item_id}", response_model=schemas.ItemResponse, tags=["Items"])
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific item by ID"""
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

# ORDER ENDPOINTS
@app.get("/orders", response_model=List[schemas.OrderResponse], tags=["Orders"])
def get_all_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all orders (sales transactions)"""
    orders = crud.get_orders(db, skip=skip, limit=limit)
    return orders

@app.post("/orders", response_model=schemas.OrderResponse, tags=["Orders"])
def add_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    """Add a new order (purchase)"""
    try:
        return crud.create_order(db=db, order=order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/orders/{order_id}", response_model=schemas.OrderResponse, tags=["Orders"])
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a specific order by ID"""
    db_order = crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.put("/orders/{order_id}", response_model=schemas.OrderResponse, tags=["Orders"])
def update_order(order_id: int, order_update: schemas.OrderUpdate, db: Session = Depends(get_db)):
    """Update an order (quantity, status, customer info)"""
    try:
        db_order = crud.update_order(db=db, order_id=order_id, order_update=order_update)
        if db_order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return db_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/orders/{order_id}", tags=["Orders"])
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Delete an order"""
    db_order = crud.delete_order(db=db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


