from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize SQLAlchemy (without binding it to an app instance yet)
db = SQLAlchemy()

def create_app():
    # Initialize the Flask application
    app = Flask(__name__)
    
    # Configure the database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://admin:admin@db:5432/mydb')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the SQLAlchemy extension with the app instance
    db.init_app(app)

    # Define a model (Table) for the items within the app context
    class Item(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        price = db.Column(db.Float, nullable=False)

    # Create the tables in the database if they don't exist
    @app.before_first_request
    def create_tables():
        with app.app_context():
            db.create_all()

    # Routes for the API endpoints
    # GET: Fetch all items
    @app.route('/api/items', methods=['GET'])
    def get_items():
        items = Item.query.all()
        return jsonify([{'id': item.id, 'name': item.name, 'price': item.price} for item in items])

    # GET: Fetch a single item by ID
    @app.route('/api/items/<int:item_id>', methods=['GET'])
    def get_item(item_id):
        item = Item.query.get(item_id)
        if item:
            return jsonify({'id': item.id, 'name': item.name, 'price': item.price})
        else:
            return jsonify({'error': 'Item not found'}), 404

    # POST: Create a new item
    @app.route('/api/items', methods=['POST'])
    def create_item():
        data = request.get_json()
        if 'name' in data and 'price' in data:
            new_item = Item(name=data['name'], price=data['price'])
            db.session.add(new_item)
            db.session.commit()
            return jsonify({'id': new_item.id, 'name': new_item.name, 'price': new_item.price}), 201
        return jsonify({'error': 'Bad request, missing name or price'}), 400

    # PUT: Update an existing item
    @app.route('/api/items/<int:item_id>', methods=['PUT'])
    def update_item(item_id):
        item = Item.query.get(item_id)
        if item:
            data = request.get_json()
            item.name = data.get('name', item.name)
            item.price = data.get('price', item.price)
            db.session.commit()
            return jsonify({'id': item.id, 'name': item.name, 'price': item.price})
        return jsonify({'error': 'Item not found'}), 404

    # DELETE: Delete an item
    @app.route('/api/items/<int:item_id>', methods=['DELETE'])
    def delete_item(item_id):
        item = Item.query.get(item_id)
        if item:
            db.session.delete(item)
            db.session.commit()
            return jsonify({'message': f'Item {item_id} deleted successfully'}), 200
        return jsonify({'error': 'Item not found'}), 404

    return app

# Run the application only if this script is executed directly
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
