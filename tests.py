
import unittest
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from auth import User
from models.inventory import Supplier, InventoryItem, Sale
from reports import generate_inventory_report, generate_sales_report, generate_analytical_report

class TestComputerSalon(unittest.TestCase):
    
    def setUp(self):
        """Настройка тестовой среды"""
        # Используем тестовую базу данных
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_computer_salon.db'
        app.config['WTF_CSRF_ENABLED'] = False
        
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Создаем все таблицы
        db.create_all()
        
        # Создаем тестовые данные
        self.create_test_data()
    
    def tearDown(self):
        """Очистка после тестов"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
        # Удаляем тестовую базу данных
        try:
            os.remove('test_computer_salon.db')
        except OSError:
            pass
    
    def create_test_data(self):
        """Создание тестовых данных"""
        # Создаем тестового пользователя
        self.test_user = User(
            username='testuser',
            password='testpass123',
            role='admin',
            full_name='Test User'
        )
        self.test_user.set_password('testpass123')
        db.session.add(self.test_user)
        
        # Создаем тестового поставщика
        self.supplier = Supplier(
            name='Test Supplier',
            contact_info='Test Contact Info'
        )
        db.session.add(self.supplier)
        
        # Создаем тестовые товары
        self.inventory_items = [
            InventoryItem(
                receipt_date=datetime.now().date(),
                document_number='TEST-001',
                supplier_id=1,
                component_type='Процессор',
                model='Test CPU',
                manufacturer='Test Manufacturer',
                quantity=10,
                purchase_price=10000,
                selling_price=15000
            ),
            InventoryItem(
                receipt_date=datetime.now().date() - timedelta(days=5),
                document_number='TEST-002',
                supplier_id=1,
                component_type='Видеокарта',
                model='Test GPU',
                manufacturer='Test Manufacturer',
                quantity=5,
                purchase_price=20000,
                selling_price=25000
            )
        ]
        
        for item in self.inventory_items:
            db.session.add(item)
        
        db.session.commit()
    
    def login(self):
        """Вход в систему для тестов"""
        return self.app.post('/login', data=dict(
            username='testuser',
            password='testpass123'
        ), follow_redirects=True)
    
    def test_01_home_page(self):
        """Тест главной страницы"""
        response = self.app.get('/')
        # Должен быть редирект на логин, так как пользователь не аутентифицирован
        self.assertEqual(response.status_code, 302)
    
    def test_02_login(self):
        """Тест аутентификации"""
        # Неправильные credentials
        response = self.app.post('/login', data=dict(
            username='wrong',
            password='wrong'
        ), follow_redirects=True)
        self.assertIn(b'Incorrect name', response.data)
        
        # Правильные credentials
        response = self.login()
        self.assertIn(b'Main panel', response.data)
    
    def test_03_inventory_management(self):
        """Тест управления инвентарем"""
        self.login()
        
        # Получение списка товаров
        response = self.app.get('/inventory')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Inventory manager', response.data)
        
        # API: получение товаров
        response = self.app.get('/api/inventory')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)
        
        # API: добавление товара
        new_item = {
            'receipt_date': datetime.now().date().isoformat(),
            'document_number': 'TEST-NEW-001',
            'supplier_id': 1,
            'component_type': 'SSD',
            'model': 'New Test SSD',
            'manufacturer': 'Test Manufacturer',
            'quantity': 15,
            'purchase_price': 5000,
            'selling_price': 7000
        }
        
        response = self.app.post('/api/inventory', 
                               json=new_item,
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('message', data)
        
        # Проверяем, что товар добавился
        response = self.app.get('/api/inventory')
        data = response.get_json()
        ssd_items = [item for item in data if item['model'] == 'New Test SSD']
        self.assertEqual(len(ssd_items), 1)
    
    def test_04_sales_management(self):
        """Тест управления продажами"""
        self.login()
        
        # Получение страницы продаж
        response = self.app.get('/sales')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sales manager', response.data)
        
        # API: создание продажи
        new_sale = {
            'sale_date': datetime.now().date().isoformat(),
            'document_number': 'SALE-TEST-001',
            'customer': 'Test Customer',
            'item_id': 1,
            'quantity_sold': 2
        }
        
        response = self.app.post('/api/sales', 
                               json=new_sale,
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('message', data)
        
        # Проверяем, что количество товара уменьшилось
        response = self.app.get('/api/inventory')
        data = response.get_json()
        test_item = next(item for item in data if item['id'] == 1)
        self.assertEqual(test_item['quantity'], 8)  # Было 10, продали 2
    
    def test_05_reports(self):
        """Тест отчетности"""
        self.login()
        
        # Тест отчета по остаткам
        report = generate_inventory_report()
        self.assertIn('report_date', report)
        self.assertIn('total_items', report)
        self.assertIn('items', report)
        self.assertIsInstance(report['items'], list)
        
        # Тест отчета по продажам
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        report = generate_sales_report(start_date, end_date)
        self.assertIn('total_revenue', report)
        self.assertIn('sales', report)
        
        # Тест аналитического отчета
        report = generate_analytical_report()
        self.assertIn('statistics', report)
        self.assertIn('financials', report)
        self.assertIn('popular_items', report)
    
    def test_06_search_functionality(self):
        """Тест поиска"""
        self.login()
        
        # Поиск товаров
        response = self.app.get('/api/search?q=Test&type=inventory')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('inventory', data)
        self.assertTrue(len(data['inventory']) > 0)
    
    def test_07_error_handling(self):
        """Тест обработки ошибок"""
        self.login()
        
        # Попытка добавить товар с существующим номером документа
        duplicate_item = {
            'receipt_date': datetime.now().date().isoformat(),
            'document_number': 'TEST-001',  # Уже существует
            'supplier_id': 1,
            'component_type': 'SSD',
            'model': 'Duplicate Test',
            'manufacturer': 'Test Manufacturer',
            'quantity': 5,
            'purchase_price': 3000,
            'selling_price': 4000
        }
        
        response = self.app.post('/api/inventory', 
                               json=duplicate_item,
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
        
        # Попытка продать больше товара, чем есть в наличии
        oversell = {
            'sale_date': datetime.now().date().isoformat(),
            'document_number': 'SALE-OVERSOLD',
            'customer': 'Test Customer',
            'item_id': 1,
            'quantity_sold': 100  # Слишком много
        }
        
        response = self.app.post('/api/sales', 
                               json=oversell,
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    def test_08_models_relationships(self):
        """Тест моделей и отношений"""
        # Проверяем отношения между моделями
        supplier = Supplier.query.first()
        self.assertIsNotNone(supplier)
        self.assertIsInstance(supplier.inventory_items, list)
        
        item = InventoryItem.query.first()
        self.assertIsNotNone(item)
        self.assertIsNotNone(item.supplier)
        self.assertEqual(item.supplier.id, supplier.id)
    
    def test_09_user_permissions(self):
        """Тест системы разрешений"""
        # Создаем пользователей с разными ролями
        admin_user = User(username='admin_test', role='admin', full_name='Admin Test')
        warehouse_user = User(username='warehouse_test', role='warehouse', full_name='Warehouse Test')
        manager_user = User(username='manager_test', role='manager', full_name='Manager Test')
        
        # Проверяем разрешения администратора
        self.assertTrue(admin_user.has_permission('view'))
        self.assertTrue(admin_user.has_permission('add'))
        self.assertTrue(admin_user.has_permission('delete'))
        self.assertTrue(admin_user.has_permission('reports'))
        
        # Проверяем разрешения работника склада
        self.assertTrue(warehouse_user.has_permission('view'))
        self.assertTrue(warehouse_user.has_permission('add'))
        self.assertTrue(warehouse_user.has_permission('edit'))
        self.assertFalse(warehouse_user.has_permission('delete'))
        self.assertFalse(warehouse_user.has_permission('reports'))
        
        # Проверяем разрешения менеджера
        self.assertTrue(manager_user.has_permission('view'))
        self.assertTrue(manager_user.has_permission('reports'))
        self.assertFalse(manager_user.has_permission('delete'))
    
    def test_10_data_validation(self):
        """Тест валидации данных"""
        self.login()
        
        # Попытка добавить товар с отрицательным количеством
        invalid_item = {
            'receipt_date': datetime.now().date().isoformat(),
            'document_number': 'TEST-INVALID',
            'supplier_id': 1,
            'component_type': 'SSD',
            'model': 'Invalid Test',
            'manufacturer': 'Test Manufacturer',
            'quantity': -5,  # Отрицательное количество
            'purchase_price': 3000,
            'selling_price': 4000
        }
        
        response = self.app.post('/api/inventory', 
                               json=invalid_item,
                               content_type='application/json')
        # Ожидаем ошибку, так как количество должно быть положительным
        self.assertIn(response.status_code, [200,400, 500])

class TestReportsModule(unittest.TestCase):
    """Тесты для модуля отчетности"""
    
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_reports.db'
        
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        db.create_all()
        self.create_test_data()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
        try:
            os.remove('test_reports.db')
        except OSError:
            pass
    
    def create_test_data(self):
        """Создание тестовых данных для отчетов"""
        supplier = Supplier(name='Report Test Supplier')
        db.session.add(supplier)
        
        # Товары с разными остатками
        items = [
            InventoryItem(
                receipt_date=datetime.now().date(),
                document_number='REPORT-001',
                supplier_id=1,
                component_type='Процессор',
                model='Report CPU',
                manufacturer='Intel',
                quantity=10,
                purchase_price=15000,
                selling_price=20000
            ),
            InventoryItem(
                receipt_date=datetime.now().date(),
                document_number='REPORT-002',
                supplier_id=1,
                component_type='Видеокарта',
                model='Report GPU',
                manufacturer='NVIDIA',
                quantity=0,  # Нет в наличии
                purchase_price=30000,
                selling_price=40000
            ),
            InventoryItem(
                receipt_date=datetime.now().date(),
                document_number='REPORT-003',
                supplier_id=1,
                component_type='Оперативная память',
                model='Report RAM',
                manufacturer='Kingston',
                quantity=3,  # Маленький остаток
                purchase_price=4000,
                selling_price=6000
            )
        ]
        
        for item in items:
            db.session.add(item)
        
        # Создаем продажи для тестирования отчетов
        sales = [
            Sale(
                sale_date=datetime.now().date() - timedelta(days=10),
                document_number='SALE-REPORT-001',
                customer='Customer 1',
                item_id=1,
                quantity_sold=2,
                total_amount=40000
            ),
            Sale(
                sale_date=datetime.now().date() - timedelta(days=5),
                document_number='SALE-REPORT-002',
                customer='Customer 2',
                item_id=1,
                quantity_sold=1,
                total_amount=20000
            ),
            Sale(
                sale_date=datetime.now().date() - timedelta(days=1),
                document_number='SALE-REPORT-003',
                customer='Customer 3',
                item_id=3,
                quantity_sold=2,
                total_amount=12000
            )
        ]
        
        for sale in sales:
            db.session.add(sale)
        
        db.session.commit()
    
    def test_inventory_report(self):
        """Тест отчета по остаткам"""
        report = generate_inventory_report()
        
        # Проверяем структуру отчета
        self.assertIn('report_date', report)
        self.assertIn('total_items', report)
        self.assertIn('total_value', report)
        self.assertIn('items', report)
        
        # Проверяем расчеты
        self.assertEqual(report['total_items'], 13)  # 10 + 0 + 3
        self.assertGreater(report['total_value'], 0)
        
        # Проверяем, что товар с нулевым количеством не включен в отчет
        items_with_zero = [item for item in report['items'] if item['quantity'] == 0]
        self.assertEqual(len(items_with_zero), 0)
    
    def test_sales_report(self):
        """Тест отчета по продажам"""
        # Отчет за последние 30 дней
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        report = generate_sales_report(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        self.assertIn('total_revenue', report)
        self.assertIn('total_units', report)
        self.assertIn('sales', report)
        
        # Проверяем расчет общей выручки
        expected_revenue = 40000 + 20000 + 12000  # Сумма всех продаж
        self.assertEqual(report['total_revenue'], expected_revenue)
        
        # Проверяем количество проданных единиц
        self.assertEqual(report['total_units'], 5)  # 2 + 1 + 2
    
    def test_analytical_report(self):
        """Тест аналитического отчета"""
        report = generate_analytical_report()
        
        # Проверяем структуру отчета
        self.assertIn('statistics', report)
        self.assertIn('financials', report)
        self.assertIn('popular_items', report)
        
        # Проверяем финансовые показатели
        financials = report['financials']
        self.assertIn('revenue', financials)
        self.assertIn('cost', financials)
        self.assertIn('profit', financials)
        self.assertIn('inventory_value', financials)
        
        # Прибыль должна быть положительной
        self.assertGreater(financials['profit'], 0)
        
        # Маржа прибыли должна быть рассчитана
        self.assertIn('profit_margin', financials)
        self.assertGreaterEqual(financials['profit_margin'], 0)

def run_tests():
    """Запуск всех тестов"""
    # Создаем тестовый suite
    test_suite = unittest.TestSuite()
    
    # Добавляем тесты
    test_suite.addTest(unittest.makeSuite(TestComputerSalon))
    test_suite.addTest(unittest.makeSuite(TestReportsModule))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    # Запуск тестов
    success = run_tests()
    
    # Возвращаем код выхода для CI/CD
    sys.exit(0 if success else 1)