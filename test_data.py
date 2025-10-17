# test_data.py
"""
Тестовые данные для проверки системы
"""

test_products = [
    {
        'id': 1,
        'name': 'Процессор Intel Core i7-13700K',
        'type': 'Процессор', 
        'manufacturer': 'Intel',
        'model': 'Core i7-13700K',
        'quantity': 15,
        'purchase_price': 25000,
        'selling_price': 32000,
        'supplier': 'ООО "Компьютерные технологии"'
    },
    {
        'id': 2,
        'name': 'Видеокарта NVIDIA RTX 4070',
        'type': 'Видеокарта',
        'manufacturer': 'NVIDIA', 
        'model': 'RTX 4070',
        'quantity': 8,
        'purchase_price': 45000,
        'selling_price': 55000,
        'supplier': 'АО "Электрон"'
    },
    {
        'id': 3,
        'name': 'Оперативная память Kingston DDR4 16GB',
        'type': 'Оперативная память',
        'manufacturer': 'Kingston',
        'model': 'DDR4 16GB 3200MHz',
        'quantity': 25, 
        'purchase_price': 4000,
        'selling_price': 5500,
        'supplier': 'ИП Иванов'
    }
]

test_sales = [
    {
        'id': 1,
        'product_id': 1,
        'product_name': 'Процессор Intel Core i7-13700K',
        'quantity': 2,
        'unit_price': 32000,
        'total_amount': 64000,
        'customer': 'ООО "ТехноСервис"',
        'date': '2024-01-15'
    },
    {
        'id': 2, 
        'product_id': 2,
        'product_name': 'Видеокарта NVIDIA RTX 4070',
        'quantity': 1,
        'unit_price': 55000,
        'total_amount': 55000,
        'customer': 'ИП Петров',
        'date': '2024-01-16'
    },
    {
        'id': 3,
        'product_id': 3,
        'product_name': 'Оперативная память Kingston DDR4 16GB',
        'quantity': 5,
        'unit_price': 5500, 
        'total_amount': 27500,
        'customer': 'ООО "Компьютерный центр"',
        'date': '2024-01-17'
    }
]

test_suppliers = [
    {
        'id': 1,
        'name': 'ООО "Компьютерные технологии"',
        'contact': 'г. Москва, ул. Ленина, 1\nтел: +7 (495) 123-45-67',
        'products_supplied': ['Процессоры', 'Материнские платы']
    },
    {
        'id': 2, 
        'name': 'АО "Электрон"',
        'contact': 'г. Санкт-Петербург, ул. Пушкина, 5\nтел: +7 (812) 987-65-43',
        'products_supplied': ['Видеокарты', 'Мониторы']
    },
    {
        'id': 3,
        'name': 'ИП Иванов',
        'contact': 'г. Новосибирск, ул. Мира, 10\nтел: +7 (383) 456-78-90',
        'products_supplied': ['Оперативная память', 'SSD']
    }
]

def calculate_total_inventory_value():
    """Расчет общей стоимости инвентаря"""
    total = sum(p['quantity'] * p['purchase_price'] for p in test_products)
    return total

def calculate_total_sales_revenue():
    """Расчет общей выручки от продаж"""
    total = sum(s['total_amount'] for s in test_sales)
    return total

def get_low_stock_products(threshold=5):
    """Получение товаров с низким запасом"""
    return [p for p in test_products if p['quantity'] < threshold]

if __name__ == '__main__':
    print("📊 ТЕСТОВЫЕ ДАННЫЕ СИСТЕМЫ")
    print("=" * 50)
    
    print(f"Количество товаров: {len(test_products)}")
    print(f"Количество продаж: {len(test_sales)}") 
    print(f"Количество поставщиков: {len(test_suppliers)}")
    print(f"Общая стоимость инвентаря: {calculate_total_inventory_value():,} руб.")
    print(f"Общая выручка от продаж: {calculate_total_sales_revenue():,} руб.")
    
    low_stock = get_low_stock_products()
    print(f"Товары с низким запасом: {len(low_stock)}")
    
    print("=" * 50)