from datetime import datetime
from database import db

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InventoryItem(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    receipt_date = db.Column(db.Date, nullable=False)
    document_number = db.Column(db.String(50), nullable=False, unique=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    component_type = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    manufacturer = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)  # Убедимся, что это Integer
    purchase_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    supplier = db.relationship('Supplier', backref='inventory_items')
    
    def to_dict(self):
        """Сериализация в словарь для API"""
        return {
            'id': self.id,
            'receipt_date': self.receipt_date.isoformat() if self.receipt_date else None,
            'document_number': self.document_number,
            'supplier_id': self.supplier_id,
            'component_type': self.component_type,
            'model': self.model,
            'manufacturer': self.manufacturer,
            'quantity': int(self.quantity),  # Гарантируем int
            'purchase_price': float(self.purchase_price),
            'selling_price': float(self.selling_price)
        }

class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    sale_date = db.Column(db.Date, nullable=False)
    document_number = db.Column(db.String(50), nullable=False, unique=True)
    customer = db.Column(db.String(100), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory.id', ondelete='RESTRICT'))
    quantity_sold = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    inventory_item = db.relationship('InventoryItem', backref='sales')