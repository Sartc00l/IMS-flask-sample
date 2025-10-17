from database import db
from auth import User
from models.inventory import Supplier, InventoryItem
from app import app
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def init_database():
    with app.app_context():
        # Создаем все таблицы
        db.create_all()
        
        # Создаем начальных пользователей с разными ролями
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin', 
                password=generate_password_hash('admin123'), 
                role='admin',
                full_name='Администратор Системы'
            )
            admin.password = generate_password_hash('admin123')
            db.session.add(admin)
        
        if not User.query.filter_by(username='warehouse').first():
            warehouse = User(
                username='warehouse', 
                password=generate_password_hash('warehouse123'), 
                role='warehouse',
                full_name='Работник Склада'
            )
            warehouse.password = generate_password_hash('warehouse123')
            db.session.add(warehouse)
        
        if not User.query.filter_by(username='manager').first():
            manager = User(
                username='manager', 
                password=generate_password_hash('manager123'), 
                role='manager',
                full_name='Менеджер Компании'
            )
            manager.password = generate_password_hash('manager123')
            db.session.add(manager)
        
        # Добавляем тестовых поставщиков
        suppliers_data = [
            {'name': 'ООО "Компьютерные технологии"', 'contact_info': 'г. Москва, ул. Ленина, 1\nтел: +7 (495) 123-45-67'},
            {'name': 'АО "Электрон"', 'contact_info': 'г. Санкт-Петербург, ул. Пушкина, 5\nтел: +7 (812) 987-65-43'},
            {'name': 'ИП Иванов', 'contact_info': 'г. Новосибирск, ул. Мира, 10\nтел: +7 (383) 456-78-90'},
            {'name': 'ЗАО "ТехноПрофи"', 'contact_info': 'г. Екатеринбург, пр. Космонавтов, 15\nтел: +7 (343) 111-22-33'}
        ]
        
        for supplier_data in suppliers_data:
            if not Supplier.query.filter_by(name=supplier_data['name']).first():
                supplier = Supplier(
                    name=supplier_data['name'],
                    contact_info=supplier_data['contact_info']
                )
                db.session.add(supplier)
        
        # Добавляем тестовые товары
        inventory_data = [
            {
                'receipt_date': datetime.now() - timedelta(days=30),
                'document_number': 'ПОСТ-001',
                'supplier_id': 1,
                'component_type': 'Процессор',
                'model': 'Core i7-13700K',
                'manufacturer': 'Intel',
                'quantity': 10,
                'purchase_price': 25000,
                'selling_price': 32000
            },
            {
                'receipt_date': datetime.now() - timedelta(days=25),
                'document_number': 'ПОСТ-002',
                'supplier_id': 2,
                'component_type': 'Видеокарта',
                'model': 'RTX 4070',
                'manufacturer': 'NVIDIA',
                'quantity': 5,
                'purchase_price': 45000,
                'selling_price': 55000
            },
            {
                'receipt_date': datetime.now() - timedelta(days=20),
                'document_number': 'ПОСТ-003',
                'supplier_id': 3,
                'component_type': 'Оперативная память',
                'model': 'DDR4 16GB',
                'manufacturer': 'Kingston',
                'quantity': 20,
                'purchase_price': 4000,
                'selling_price': 5500
            }
        ]
        
        for item_data in inventory_data:
            if not InventoryItem.query.filter_by(document_number=item_data['document_number']).first():
                item = InventoryItem(**item_data)
                db.session.add(item)
        
        # Сохраняем изменения
        db.session.commit()
        
        print("=" * 50)
        print("БАЗА ДАННЫХ УСПЕШНО ИНИЦИАЛИЗИРОВАНА!")
        print("=" * 50)
        print("Созданы пользователи для входа в систему:")
        print("  Администратор: admin / admin123")
        print("  Работник склада: warehouse / warehouse123")
        print("  Менеджер: manager / manager123")
        print("=" * 50)

if __name__ == '__main__':
    init_database()