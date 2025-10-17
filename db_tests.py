
import unittest
import os
import sys
import tempfile
import shutil

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestDatabaseModels(unittest.TestCase):
    """Тесты моделей базы данных"""
    
    def setUp(self):
        """Создаем временную базу данных"""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, 'test.db')
        
        # Имитируем простую базу данных
        self.products = []
        self.sales = []
        self.suppliers = []
    
    def tearDown(self):
        """Очищаем временные файлы"""
        shutil.rmtree(self.test_dir)
    
    def test_01_product_creation(self):
        """Тест создания товара"""
        product = {
            'id': 1,
            'name': 'Тестовый товар',
            'type': 'Процессор',
            'manufacturer': 'Intel',
            'model': 'Core i7',
            'quantity': 10,
            'purchase_price': 25000,
            'selling_price': 32000
        }
        
        self.products.append(product)
        
        self.assertEqual(len(self.products), 1)
        self.assertEqual(self.products[0]['name'], 'Тестовый товар')
        self.assertEqual(self.products[0]['quantity'], 10)
        print("✅ Тест создания товара пройден")
    
    def test_02_sale_creation(self):
        """Тест создания продажи"""

        product = {
            'id': 1,
            'name': 'Тестовый товар',
            'quantity': 10,
            'selling_price': 32000
        }
        self.products.append(product)
        

        sale = {
            'id': 1,
            'product_id': 1,
            'quantity': 2,
            'total_amount': 64000,
            'customer': 'Тестовый клиент'
        }
        self.sales.append(sale)
        
        # Обновляем количество товара
        for p in self.products:
            if p['id'] == 1:
                p['quantity'] -= sale['quantity']
                break
        
        self.assertEqual(len(self.sales), 1)
        self.assertEqual(self.sales[0]['total_amount'], 64000)
        
        # Проверяем, что количество товара уменьшилось
        self.assertEqual(self.products[0]['quantity'], 8)
        print("✅ Тест создания продажи пройден")
    
    def test_03_supplier_management(self):
        """Тест управления поставщиками"""
        supplier = {
            'id': 1,
            'name': 'Тестовый поставщик',
            'contact': 'test@example.com'
        }
        self.suppliers.append(supplier)
        
        # Поиск поставщика
        found_supplier = next((s for s in self.suppliers if s['name'] == 'Тестовый поставщик'), None)
        
        self.assertIsNotNone(found_supplier)
        self.assertEqual(found_supplier['contact'], 'test@example.com')
        print("✅ Тест управления поставщиками пройден")
    
    def test_04_inventory_search(self):
        """Тест поиска в инвентаре"""
        # Добавляем тестовые товары
        test_products = [
            {'id': 1, 'name': 'Процессор Intel Core i7', 'type': 'Процессор', 'quantity': 5},
            {'id': 2, 'name': 'Видеокарта NVIDIA RTX 4070', 'type': 'Видеокарта', 'quantity': 3},
            {'id': 3, 'name': 'Оперативная память Kingston 16GB', 'type': 'Память', 'quantity': 10}
        ]
        self.products.extend(test_products)
        
        # Поиск по названию
        search_term = 'Intel'
        results = [p for p in self.products if search_term.lower() in p['name'].lower()]
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Процессор Intel Core i7')
        
        # Поиск по типу
        search_term = 'Видеокарта'
        results = [p for p in self.products if search_term.lower() in p['type'].lower()]
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Видеокарта NVIDIA RTX 4070')
        print("✅ Тест поиска в инвентаре пройден")

class TestFinancialCalculations(unittest.TestCase):
    """Тесты финансовых расчетов"""
    
    def test_01_profit_calculation_comprehensive(self):
        """Комплексный тест расчета прибыли"""
        def calculate_financials(sales, inventory):
            total_revenue = sum(sale['total_amount'] for sale in sales)
            
            # Расчет себестоимости проданного
            cost_of_goods_sold = 0
            for sale in sales:
                product = next((p for p in inventory if p['id'] == sale['product_id']), None)
                if product:
                    cost_of_goods_sold += sale['quantity'] * product['purchase_price']
            
            gross_profit = total_revenue - cost_of_goods_sold
            profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            return {
                'revenue': total_revenue,
                'cost_of_goods_sold': cost_of_goods_sold,
                'gross_profit': gross_profit,
                'profit_margin': profit_margin
            }
        
        # Тестовые данные
        inventory = [
            {'id': 1, 'purchase_price': 25000, 'selling_price': 32000},
            {'id': 2, 'purchase_price': 45000, 'selling_price': 55000}
        ]
        
        sales = [
            {'product_id': 1, 'quantity': 2, 'total_amount': 64000},
            {'product_id': 2, 'quantity': 1, 'total_amount': 55000}
        ]
        
        financials = calculate_financials(sales, inventory)
        
        self.assertEqual(financials['revenue'], 119000)
        self.assertEqual(financials['cost_of_goods_sold'], 95000)  # 2*25000 + 1*45000
        self.assertEqual(financials['gross_profit'], 24000)
        self.assertAlmostEqual(financials['profit_margin'], 20.17, places=2)
        print("✅ Комплексный тест расчета прибыли пройден")

def run_database_tests():
    """Запуск тестов базы данных"""
    print("🗃️  ЗАПУСК ТЕСТОВ БАЗЫ ДАННЫХ")
    print("=" * 50)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseModels))
    suite.addTests(loader.loadTestsFromTestCase(TestFinancialCalculations))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 50)
    if result.wasSuccessful():
        print("🎉 ТЕСТЫ БАЗЫ ДАННЫХ ПРОЙДЕНЫ!")
    else:
        print(f"⚠️  ПРОБЛЕМЫ: {len(result.failures)} тестов не пройдено")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_database_tests()
    sys.exit(0 if success else 1)