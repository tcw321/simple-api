import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models import Item

def test_create_item(client: TestClient, test_db: Session):
    # Test creating an item
    response = client.post(
        "/items/",
        json={"name": "test item"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test item"
    assert "id" in data
    
    # Verify item was created in database
    db_item = test_db.query(Item).filter(Item.id == data["id"]).first()
    assert db_item is not None
    assert db_item.name == "test item"

def test_read_item(client: TestClient, test_db: Session):
    # Create test item in database
    db_item = Item(name="test read item")
    test_db.add(db_item)
    test_db.commit()
    test_db.refresh(db_item)
    
    # Test reading the item
    response = client.get(f"/items/{db_item.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test read item"
    assert data["id"] == db_item.id

def test_read_nonexistent_item(client: TestClient):
    response = client.get("/items/999")
    assert response.status_code == 404

def test_create_invalid_item(client: TestClient):
    response = client.post(
        "/items/",
        json={"invalid_field": "test"}
    )
    assert response.status_code == 422  # Validation error
