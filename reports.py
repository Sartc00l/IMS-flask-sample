from datetime import datetime, timedelta
from database import db
from models.inventory import InventoryItem, Sale
from sqlalchemy import func, extract

def generate_inventory_report():
    """Отчет по остаткам на складе"""
    items = InventoryItem.query.filter(InventoryItem.quantity > 0).all()
    
    total_value = sum(item.quantity * item.purchase_price for item in items)
    total_items = sum(item.quantity for item in items)
    
    return {
        'report_date': datetime.now().strftime('%d.%m.%Y %H:%M'),
        'total_items': total_items,
        'total_value': round(total_value, 2),
        'items': [{
            'id': item.id,
            'component_type': item.component_type,
            'model': item.model,
            'manufacturer': item.manufacturer,
            'quantity': item.quantity,
            'purchase_price': item.purchase_price,
            'value': round(item.quantity * item.purchase_price, 2)
        } for item in items]
    }

def generate_sales_report(start_date=None, end_date=None):
    """Отчет по продажам за период"""
    query = Sale.query
    
    if start_date:
        query = query.filter(Sale.sale_date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Sale.sale_date <= datetime.strptime(end_date, '%Y-%m-%d'))
    
    sales = query.all()
    
    total_revenue = sum(sale.total_amount for sale in sales)
    total_units = sum(sale.quantity_sold for sale in sales)
    total_cost = sum(sale.quantity_sold * sale.inventory_item.purchase_price for sale in sales)
    total_profit = total_revenue - total_cost
    
    return {
        'period': f"{start_date} - {end_date}" if start_date and end_date else "Все время",
        'total_revenue': round(total_revenue, 2),
        'total_units': total_units,
        'total_cost': round(total_cost, 2),
        'total_profit': round(total_profit, 2),
        'sales': [{
            'id': sale.id,
            'sale_date': sale.sale_date.strftime('%d.%m.%Y'),
            'document_number': sale.document_number,
            'customer': sale.customer,
            'product': f"{sale.inventory_item.manufacturer} {sale.inventory_item.model}",
            'quantity': sale.quantity_sold,
            'unit_price': sale.inventory_item.selling_price,
            'revenue': sale.total_amount
        } for sale in sales]
    }

def generate_quarterly_sales_report(year=None, quarter=None):
    """Отчет по продажам за квартал"""
    if not year:
        year = datetime.now().year
    
    if quarter == 1:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 3, 31)
    elif quarter == 2:
        start_date = datetime(year, 4, 1)
        end_date = datetime(year, 6, 30)
    elif quarter == 3:
        start_date = datetime(year, 7, 1)
        end_date = datetime(year, 9, 30)
    elif quarter == 4:
        start_date = datetime(year, 10, 1)
        end_date = datetime(year, 12, 31)
    else:
        # Текущий квартал
        current_month = datetime.now().month
        quarter = (current_month - 1) // 3 + 1
        return generate_quarterly_sales_report(year, quarter)
    
    return generate_sales_report(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

def generate_analytical_report():
    """Аналитический отчет для руководства"""
    # Общая статистика
    total_items = InventoryItem.query.count()
    total_sales = Sale.query.count()
    total_suppliers = db.session.query(InventoryItem.supplier_id).distinct().count()
    
    # Финансовые показатели
    sales = Sale.query.all()
    revenue = sum(sale.total_amount for sale in sales)
    cost = sum(sale.quantity_sold * sale.inventory_item.purchase_price for sale in sales)
    profit = revenue - cost
    
    # Товары на складе
    inventory_items = InventoryItem.query.all()
    inventory_value = sum(item.quantity * item.purchase_price for item in inventory_items)
    potential_revenue = sum(item.quantity * item.selling_price for item in inventory_items)
    potential_profit = potential_revenue - inventory_value
    
    # Популярные товары
    popular_items = db.session.query(
        InventoryItem.manufacturer,
        InventoryItem.model,
        func.sum(Sale.quantity_sold).label('total_sold')
    ).join(Sale).group_by(InventoryItem.id).order_by(func.sum(Sale.quantity_sold).desc()).limit(5).all()
    
    return {
        'report_date': datetime.now().strftime('%d.%m.%Y %H:%M'),
        'statistics': {
            'total_items': total_items,
            'total_sales': total_sales,
            'total_suppliers': total_suppliers
        },
        'financials': {
            'revenue': round(revenue, 2),
            'cost': round(cost, 2),
            'profit': round(profit, 2),
            'inventory_value': round(inventory_value, 2),
            'potential_revenue': round(potential_revenue, 2),
            'potential_profit': round(potential_profit, 2),
            'profit_margin': round((profit / revenue * 100) if revenue > 0 else 0, 2)
        },
        'popular_items': [{
            'product': f"{item.manufacturer} {item.model}",
            'total_sold': item.total_sold
        } for item in popular_items]
    }