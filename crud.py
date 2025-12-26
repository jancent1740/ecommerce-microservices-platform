from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import models
import schemas


# Utility function to calculate order total
def calculate_order_total(db: Session, order_id: int):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        return 0.0

    total = 0.0
    for order_item in order.order_items:
        total += order_item.quantity * order_item.unit_price
    order.total_amount = total
    order.updated_at = datetime.utcnow()
    db.commit()
    return total


# Item CRUD operations
def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()


def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(db: Session, item_id: int, item: schemas.ItemCreate):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        for key, value in item.dict().items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item


def delete_item(db: Session, item_id: int):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item


# Order CRUD operations
def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).offset(skip).limit(limit).all()


def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def create_order(db: Session, order: schemas.OrderCreate):
    # Create the order
    db_order = models.Order(
        customer_name=order.customer_name,
        customer_email=order.customer_email
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Add order items
    for item_data in order.items:
        # Get the item to check stock and get price
        item = db.query(models.Item).filter(models.Item.id == item_data.item_id).first()
        if not item:
            # Delete the order if item doesn't exist
            db.delete(db_order)
            db.commit()
            raise ValueError(f"Item with id {item_data.item_id} not found")

        # Debug print to see what values we're comparing
        print(f"DEBUG: Item ID: {item.id}, Stock: {item.stock_quantity} (type: {type(item.stock_quantity)})")
        print(f"DEBUG: Order quantity: {item_data.quantity} (type: {type(item_data.quantity)})")
        print(f"DEBUG: Comparison result: {item.stock_quantity < item_data.quantity}")

        if item.stock_quantity < item_data.quantity:
            # Delete the order if insufficient stock
            db.delete(db_order)
            db.commit()
            raise ValueError(
                f"Insufficient stock for item {item.name}. Available: {item.stock_quantity}, Requested: {item_data.quantity}")

        # Create order item
        order_item = models.OrderItem(
            order_id=db_order.id,
            item_id=item_data.item_id,
            quantity=item_data.quantity,
            unit_price=item.price
        )
        db.add(order_item)

        # Update item stock
        print(f"DEBUG: Before stock update - Stock: {item.stock_quantity}, Subtracting: {item_data.quantity}")
        item.stock_quantity -= item_data.quantity
        print(f"DEBUG: After stock update - New stock: {item.stock_quantity}")

    db.commit()

    # Calculate total
    calculate_order_total(db, db_order.id)
    db.refresh(db_order)

    return db_order


def update_order(db: Session, order_id: int, order_update: schemas.OrderUpdate):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        return None

    # Update basic order info
    if order_update.customer_name is not None:
        db_order.customer_name = order_update.customer_name
    if order_update.customer_email is not None:
        db_order.customer_email = order_update.customer_email
    if order_update.status is not None:
        db_order.status = order_update.status

    # Update items if provided
    if order_update.items is not None:
        # First, restore stock for existing items
        for existing_item in db_order.order_items:
            item = db.query(models.Item).filter(models.Item.id == existing_item.item_id).first()
            if item:
                item.stock_quantity += existing_item.quantity

        # Remove existing order items
        db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).delete()

        # Add new order items
        for item_data in order_update.items:
            item = db.query(models.Item).filter(models.Item.id == item_data.item_id).first()
            if not item:
                raise ValueError(f"Item with id {item_data.item_id} not found")

            if item.stock_quantity < item_data.quantity:
                raise ValueError(f"Insufficient stock for item {item.name}")

            # Create new order item
            order_item = models.OrderItem(
                order_id=order_id,
                item_id=item_data.item_id,
                quantity=item_data.quantity,
                unit_price=item.price
            )
            db.add(order_item)

            # Update stock
            item.stock_quantity -= item_data.quantity

    db_order.updated_at = datetime.utcnow()
    db.commit()

    # Recalculate total
    calculate_order_total(db, order_id)
    db.refresh(db_order)

    return db_order


def delete_order(db: Session, order_id: int):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        return None

    # Restore stock for all items in the order
    for order_item in db_order.order_items:
        item = db.query(models.Item).filter(models.Item.id == order_item.item_id).first()
        if item:
            item.stock_quantity += order_item.quantity

    db.delete(db_order)
    db.commit()
    return db_order