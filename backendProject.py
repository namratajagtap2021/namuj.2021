from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transactions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the ProductTransaction model
class ProductTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    price = db.Column(db.Float)
    date_of_sale = db.Column(db.String(10))  # Format: YYYY-MM-DD
    category = db.Column(db.String(255))
    sold = db.Column(db.Boolean)

# Function to initialize the database with seed data
def initialize_database():
    # Ensure tables are created
    db.create_all()
    
    # Check if the database is empty
    if ProductTransaction.query.count() == 0:
        # Fetch data from third-party API
        url = "https://s3.amazonaws.com/roxiler.com/product_transaction.json"
        response = requests.get(url)
        data = response.json()

        # Insert data into the database
        for item in data:
            transaction = ProductTransaction(
                title=item.get('title'),
                description=item.get('description'),
                price=item.get('price'),
                date_of_sale=item.get('dateOfSale'),
                category=item.get('category'),
                sold=item.get('sold')
            )
            db.session.add(transaction)

        db.session.commit()

# Initialize database when the application starts
with app.app_context():
    initialize_database()

# Function to filter by month
def filter_by_month(month):
    month_number = datetime.strptime(month, '%B').month
    return db.session.query(ProductTransaction).filter(func.strftime('%m', ProductTransaction.date_of_sale) == str(month_number).zfill(2))

# Your other API routes and logic here...

if __name__ == '__main__':
    app.run(debug=True)
