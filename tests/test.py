# tests/test_integration.py
import pytest
from Flask_docker.app import create_app, db
from Flask_docker.app import Item  # Import the model to interact with in tests

@pytest.fixture
def app():
    # Create an instance of the app with testing configuration
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory SQLite database for testing
    app.config['TESTING'] = True
    
    # Set up the application context and initialize the database
    with app.app_context():
        db.create_all()  # Create tables in the test database

    yield app

    # Tear down the database
    with app.app_context():
        db.drop_all()  # Clean up the test database

@pytest.fixture
def client(app):
    # Provide a test client for making requests
    return app.test_client()

def test_database_connection(app):
    """Test if the database connection is successful by creating and querying an item."""
    with app.app_context():
        # Create a sample item in the test database
        item = Item(name="Sample Item", price=9.99)
        db.session.add(item)
        db.session.commit()
        
        # Query the item to ensure it was added successfully
        queried_item = Item.query.filter_by(name="Sample Item").first()
        assert queried_item is not None
        assert queried_item.name == "Sample Item"
        assert queried_item.price == 9.99

def test_get_items(client, app):
    """Test the /api/items endpoint to check if it fetches data from the database correctly."""
    with app.app_context():
        # Add a sample item to the database
        item = Item(name="Test Item", price=10.0)
        db.session.add(item)
        db.session.commit()

    # Call the /api/items endpoint
    response = client.get('/api/items')
    assert response.status_code == 200  # Ensure that the response is successful
    
    # Verify that the response contains the item we added
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['name'] == "Test Item"
    assert data[0]['price'] == 10.0
