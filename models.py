from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    product_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to movements
    movements = db.relationship('ProductMovement', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.product_id}: {self.name} (qty: {self.quantity})>'

class Location(db.Model):
    location_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships to movements
    movements_from = db.relationship('ProductMovement', foreign_keys='ProductMovement.from_location', backref='from_loc', lazy=True)
    movements_to = db.relationship('ProductMovement', foreign_keys='ProductMovement.to_location', backref='to_loc', lazy=True)
    
    def __repr__(self):
        return f'<Location {self.location_id}: {self.name}>'

class ProductMovement(db.Model):
    movement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    from_location = db.Column(db.String(50), db.ForeignKey("location.location_id"), nullable=True)
    to_location = db.Column(db.String(50), db.ForeignKey("location.location_id"), nullable=True)
    product_id = db.Column(db.String(50), db.ForeignKey("product.product_id"), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Movement {self.movement_id}: {self.product_id} qty={self.qty}>'
    
    @property
    def movement_type(self):
        if self.from_location and self.to_location:
            return "Transfer"
        elif self.to_location:
            return "Stock In"
        elif self.from_location:
            return "Stock Out"
        return "Unknown"
