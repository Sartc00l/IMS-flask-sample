# simple_tests.py
import unittest
import os
import sys
from datetime import datetime, timedelta

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestBasicFunctions(unittest.TestCase):
    """Базовые тесты без зависимостей от Flask"""
    
    def test_02_date_formatting(self):
        """Тест форматирования дат"""
        test_date = datetime(2024, 1, 15)
        
        # Формат для отображения
        display_format = test_date.strftime('%d.%m.%Y')
        self.assertEqual(display_format, "15.01.2024")
        
        # Формат для input fields
        input_format = test_date.strftime('%Y-%m-%d')
        self.assertEqual(input_format, "2024-01-15")
        print("✅ Тест форматирования дат пройден")
    
    def test_03_data_validation(self):
        """Тест валидации данных"""
        # Валидация количества
        def validate_quantity(quantity_str, available):
            try:
                quantity = int(quantity_str)
                if quantity <= 0:
                    return False, "Количество должно быть больше 0"
                if quantity > available:
                    return False, f"Недостаточно товара. Доступно: {available} шт."
                return True, "OK"
            except ValueError:
                return False, "Количество должно быть числом"
        
        # Тестовые случаи
        self.assertEqual(validate_quantity("5", 10), (True, "OK"))
        self.assertEqual(validate_quantity("15", 10)[0], False)
        self.assertEqual(validate_quantity("0", 10)[0], False)
        self.assertEqual(validate_quantity("abc", 10)[0], False)
        print("✅ Тест валидации данных пройден")

class TestBusinessLogic(unittest.TestCase):
    """Тесты бизнес-логики"""
    
    def test_01_profit_calculation(self):
        """Тест расчета прибыли"""
        def calculate_profit(selling_price, purchase_price, quantity):
            revenue = selling_price * quantity
            cost = purchase_price * quantity
            profit = revenue - cost
            profit_margin = (profit / revenue * 100) if revenue > 0 else 0
            return profit, profit_margin
        
        profit, margin = calculate_profit(20000, 15000, 5)
        self.assertEqual(profit, 25000)  # (20000-15000)*5
        self.assertEqual(margin, 25.0)   # 5000/20000*100
        
        print("✅ Тест расчета прибыли пройден")
    
    def test_02_inventory_value(self):
        """Тест расчета стоимости инвентаря"""
        def calculate_inventory_value(items):
            total_value = 0
            total_items = 0
            for item in items:
                total_value += item['quantity'] * item['purchase_price']
                total_items += item['quantity']
            return total_value, total_items
        
        test_items = [
            {'quantity': 5, 'purchase_price': 10000},
            {'quantity': 3, 'purchase_price': 15000},
            {'quantity': 10, 'purchase_price': 5000}
        ]
        
        total_value, total_items = calculate_inventory_value(test_items)
        self.assertEqual(total_value, 145000)  # 5*10000 + 3*15000 + 10*5000
        self.assertEqual(total_items, 18)
        
        print("✅ Тест расчета стоимости инвентаря пройден")
    
    def test_03_sales_analysis(self):
        """Тест анализа продаж"""
        def analyze_sales(sales_data):
            total_revenue = sum(sale['amount'] for sale in sales_data)
            total_units = sum(sale['quantity'] for sale in sales_data)
            avg_sale = total_revenue / len(sales_data) if sales_data else 0
            
            return {
                'total_revenue': total_revenue,
                'total_units': total_units,
                'avg_sale': avg_sale,
                'total_sales': len(sales_data)
            }
        
        test_sales = [
            {'quantity': 2, 'amount': 40000},
            {'quantity': 1, 'amount': 20000},
            {'quantity': 3, 'amount': 45000}
        ]
        
        analysis = analyze_sales(test_sales)
        self.assertEqual(analysis['total_revenue'], 105000)
        self.assertEqual(analysis['total_units'], 6)
        self.assertEqual(analysis['avg_sale'], 35000)
        self.assertEqual(analysis['total_sales'], 3)
        
        print("✅ Тест анализа продаж пройден")

class TestReportGeneration(unittest.TestCase):
    """Тесты генерации отчетов"""
    
    def test_02_popular_products(self):
        """Тест определения популярных товаров"""
        def get_popular_products(sales, top_n=3):
            product_sales = {}
            for sale in sales:
                product = sale['product']
                if product not in product_sales:
                    product_sales[product] = 0
                product_sales[product] += sale['quantity']
            
            # Сортируем по количеству продаж
            popular = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)
            return popular[:top_n]
        
        test_sales = [
            {'product': 'Процессор', 'quantity': 5},
            {'product': 'Видеокарта', 'quantity': 3},
            {'product': 'Процессор', 'quantity': 2},
            {'product': 'Оперативная память', 'quantity': 8},
            {'product': 'Видеокарта', 'quantity': 4},
            {'product': 'SSD', 'quantity': 6},
        ]
        
        popular = get_popular_products(test_sales, 3)
        expected = [('Процессор', 7), ('Оперативная память', 8), ('Видеокарта', 7)]
        
        # Сортируем оба списка для сравнения
        popular_sorted = sorted(popular, key=lambda x: x[0])
        expected_sorted = sorted(expected, key=lambda x: x[0])
        
        self.assertEqual(popular_sorted, expected_sorted)
        print("✅ Тест популярных товаров пройден")

class TestUserPermissions(unittest.TestCase):
    """Тесты системы разрешений"""
    
    def test_01_role_permissions(self):
        """Тест разрешений для разных ролей"""
        class User:
            def __init__(self, role):
                self.role = role
            
            def has_permission(self, permission):
                permissions = {
                    'admin': ['view', 'add', 'edit', 'delete', 'reports', 'analytics'],
                    'warehouse': ['view', 'add', 'edit'],
                    'manager': ['view', 'reports', 'analytics']
                }
                return permission in permissions.get(self.role, [])
        
        # Тестируем разные роли
        admin = User('admin')
        warehouse = User('warehouse')
        manager = User('manager')
        
        # Администратор
        self.assertTrue(admin.has_permission('delete'))
        self.assertTrue(admin.has_permission('reports'))
        
        # Работник склада
        self.assertTrue(warehouse.has_permission('add'))
        self.assertTrue(warehouse.has_permission('edit'))
        self.assertFalse(warehouse.has_permission('delete'))
        self.assertFalse(warehouse.has_permission('reports'))
        
        # Менеджер
        self.assertTrue(manager.has_permission('reports'))
        self.assertTrue(manager.has_permission('analytics'))
        self.assertFalse(manager.has_permission('delete'))
        
        print("✅ Тест разрешений пройден")

def run_all_tests():
    """Запуск всех тестов"""
    print("🚀 ЗАПУСК ТЕСТОВ КОМПЬЮТЕРНОГО САЛОНА")
    print("=" * 50)
    
    # Создаем тестовый suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем тесты
    suite.addTests(loader.loadTestsFromTestCase(TestBasicFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestBusinessLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestReportGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestUserPermissions))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 50)
    if result.wasSuccessful():
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print(f"⚠️  ПРОБЛЕМЫ: {len(result.failures)} тестов не пройдено")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)   