from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import json

from database import db, init_db
from auth import User
from models.inventory import InventoryItem, Sale, Supplier
from reports import generate_inventory_report, generate_sales_report, generate_quarterly_sales_report, generate_analytical_report

app = Flask(__name__)
app.config['SECRET_KEY'] = 'computer-salon-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///computer_salon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


init_db(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def dashboard():

    total_items = InventoryItem.query.count()
    total_sales = Sale.query.count()
    low_stock = InventoryItem.query.filter(InventoryItem.quantity < 5).count()
    
    # Последние продажи
    recent_sales = Sale.query.order_by(Sale.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         total_items=total_items,
                         total_sales=total_sales,
                         low_stock=low_stock,
                         recent_sales=recent_sales,
                         now=datetime.now())


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Добро пожаловать, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))


@app.route('/inventory')
@login_required
def inventory_page():
    if not current_user.has_permission('view'):
        flash('Недостаточно прав для просмотра инвентаря', 'error')
        return redirect(url_for('dashboard'))
    
    items = InventoryItem.query.all()
    suppliers = Supplier.query.all()
    return render_template('inventory.html', items=items, suppliers=suppliers)

@app.route('/api/inventory', methods=['GET', 'POST'])
@login_required
def inventory_api():
    if request.method == 'GET':
        if not current_user.has_permission('view'):
            return jsonify({'error': 'Недостаточно прав'}), 403
        
        items = InventoryItem.query.all()
        return jsonify([{
            'id': item.id,
            'receipt_date': item.receipt_date.strftime('%Y-%m-%d'),
            'document_number': item.document_number,
            'supplier': item.supplier.name,
            'component_type': item.component_type,
            'model': item.model,
            'manufacturer': item.manufacturer,
            'quantity': item.quantity,
            'purchase_price': item.purchase_price,
            'selling_price': item.selling_price
        } for item in items])
    
    elif request.method == 'POST':
        if not current_user.has_permission('add'):
            return jsonify({'error': 'Недостаточно прав'}), 403
        
        try:
            data = request.get_json()
            

            if InventoryItem.query.filter_by(document_number=data['document_number']).first():
                return jsonify({'error': 'Товар с таким номером документа уже существует'}), 400
            
            new_item = InventoryItem(
                receipt_date=datetime.strptime(data['receipt_date'], '%Y-%m-%d').date(),
                document_number=data['document_number'],
                supplier_id=data['supplier_id'],
                component_type=data['component_type'],
                model=data['model'],
                manufacturer=data['manufacturer'],
                quantity=data['quantity'],
                purchase_price=float(data['purchase_price']),
                selling_price=float(data['selling_price'])
            )
            db.session.add(new_item)
            db.session.commit()
            return jsonify({'message': 'Товар успешно добавлен', 'id': new_item.id})
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Ошибка при добавлении товара: {str(e)}'}), 500

@app.route('/api/inventory/<int:item_id>', methods=['PUT', 'DELETE'])
@login_required
def inventory_item_api(item_id):
    item = InventoryItem.query.get_or_404(item_id)
    
    if request.method == 'PUT':
        if not current_user.has_permission('edit'):
            return jsonify({'error': 'Недостаточно прав'}), 403
        
        try:
            data = request.get_json()
            
            # Проверка уникальности номера документа (исключая текущий товар)
            if data.get('document_number') and data['document_number'] != item.document_number:
                if InventoryItem.query.filter_by(document_number=data['document_number']).first():
                    return jsonify({'error': 'Товар с таким номером документа уже существует'}), 400
            
            item.receipt_date = datetime.strptime(data['receipt_date'], '%Y-%m-%d').date()
            item.document_number = data['document_number']
            item.supplier_id = data['supplier_id']
            item.component_type = data['component_type']
            item.model = data['model']
            item.manufacturer = data['manufacturer']
            item.quantity = data['quantity']
            item.purchase_price = float(data['purchase_price'])
            item.selling_price = float(data['selling_price'])
            
            db.session.commit()
            return jsonify({'message': 'Товар успешно обновлен'})
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Ошибка при обновлении товара: {str(e)}'}), 500
    
    elif request.method == 'DELETE':
        if not current_user.has_permission('delete'):
            return jsonify({'error': 'Недостаточно прав'}), 403
        
        try:
            # Проверяем, есть ли связанные продажи
            sales_count = Sale.query.filter_by(item_id=item_id).count()
            if sales_count > 0:
                return jsonify({'error': 'Нельзя удалить товар, по которому есть продажи'}), 400
            
            db.session.delete(item)
            db.session.commit()
            return jsonify({'message': 'Товар успешно удален'})
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Ошибка при удалении товара: {str(e)}'}), 500

# Управление продажами
@app.route('/sales')
@login_required
def sales_page():
    if not current_user.has_permission('view'):
        flash('Недостаточно прав для просмотра продаж', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        sales = Sale.query.order_by(Sale.sale_date.desc()).all()
        inventory_items = InventoryItem.query.filter(InventoryItem.quantity > 0).all()
        
        return render_template('sales.html', sales=sales, inventory_items=inventory_items)
    
    except Exception as e:
        flash(f'Ошибка при загрузке данных о продажах: {str(e)}', 'error')
        return render_template('sales.html', sales=[], inventory_items=[])

@app.route('/api/sales', methods=['POST'])
@login_required
def sales_api():
    if not current_user.has_permission('add'):
        return jsonify({'error': 'Недостаточно прав'}), 403
    
    try:
        data = request.get_json()
        
        # Проверка уникальности номера документа
        if Sale.query.filter_by(document_number=data['document_number']).first():
            return jsonify({'error': 'Продажа с таким номером документа уже существует'}), 400
        
        # Получаем и проверяем товар
        item = InventoryItem.query.get(data['item_id'])
        if not item:
            return jsonify({'error': 'Товар не найден'}), 404
        
        # Преобразуем quantity_sold в int для корректного сравнения
        quantity_sold = int(data['quantity_sold'])
        item_quantity = int(item.quantity)  # убедимся, что это тоже int
        
        if item_quantity < quantity_sold:
            return jsonify({'error': f'Недостаточно товара на складе. Доступно: {item_quantity} шт.'}), 400
        
        # Преобразуем цены в float для расчетов
        selling_price = float(item.selling_price)
        total_amount = quantity_sold * selling_price
        
        new_sale = Sale(
            sale_date=datetime.strptime(data['sale_date'], '%Y-%m-%d').date(),
            document_number=data['document_number'],
            customer=data['customer'],
            item_id=int(data['item_id']),  # преобразуем в int
            quantity_sold=quantity_sold,   # уже преобразовано в int
            total_amount=total_amount
        )
        
        # Обновление количества товара (убедимся, что это int)
        item.quantity = item_quantity - quantity_sold
        
        db.session.add(new_sale)
        db.session.commit()
        
        return jsonify({
            'message': 'Продажа успешно добавлена', 
            'id': new_sale.id,
            'total_amount': total_amount
        })
    
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': f'Ошибка преобразования данных: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Ошибка при добавлении продажи: {str(e)}'}), 500

@app.route('/api/sales/<int:sale_id>', methods=['DELETE'])
@login_required
def delete_sale_api(sale_id):
    if not current_user.has_permission('delete'):
        return jsonify({'error': 'Недостаточно прав'}), 403
    
    try:
        sale = Sale.query.get_or_404(sale_id)
        
        # Возвращаем товар на склад
        item = sale.inventory_item
        if item:
            item.quantity += sale.quantity_sold
        
        db.session.delete(sale)
        db.session.commit()
        
        return jsonify({'message': 'Продажа успешно удалена'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Ошибка при удалении продажи: {str(e)}'}), 500

# Отчеты
@app.route('/reports')
@login_required
def reports_page():
    if not current_user.has_permission('reports'):
        flash('Недостаточно прав для просмотра отчетов', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('reports.html')

@app.route('/api/reports/inventory')
@login_required
def inventory_report_api():
    if not current_user.has_permission('reports'):
        return jsonify({'error': 'Недостаточно прав'}), 403
    
    report = generate_inventory_report()
    return jsonify(report)

@app.route('/api/reports/sales')
@login_required
def sales_report_api():
    if not current_user.has_permission('reports'):
        return jsonify({'error': 'Недостаточно прав'}), 403
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    quarter = request.args.get('quarter', type=int)
    year = request.args.get('year', type=int)
    
    if quarter:
        report = generate_quarterly_sales_report(year, quarter)
    else:
        report = generate_sales_report(start_date, end_date)
    
    return jsonify(report)

@app.route('/analytics')
@login_required
def analytics_page():
    if not current_user.has_permission('analytics'):
        flash('Недостаточно прав для просмотра аналитики', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('analytics.html')

@app.route('/api/analytics')
@login_required
def analytics_api():
    if not current_user.has_permission('analytics'):
        return jsonify({'error': 'Недостаточно прав'}), 403
    
    report = generate_analytical_report()
    return jsonify(report)

# Поиск
@app.route('/api/search')
@login_required
def search_api():
    if not current_user.has_permission('view'):
        return jsonify({'error': 'Недостаточно прав'}), 403
    
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')
    
    results = {}
    
    if search_type in ['all', 'inventory']:
        inventory_results = InventoryItem.query.filter(
            (InventoryItem.document_number.contains(query)) |
            (InventoryItem.model.contains(query)) |
            (InventoryItem.manufacturer.contains(query)) |
            (InventoryItem.component_type.contains(query))
        ).all()
        
        results['inventory'] = [{
            'id': item.id,
            'document_number': item.document_number,
            'model': item.model,
            'manufacturer': item.manufacturer,
            'component_type': item.component_type,
            'quantity': item.quantity
        } for item in inventory_results]
    
    if search_type in ['all', 'sales']:
        sales_results = Sale.query.filter(
            (Sale.document_number.contains(query)) |
            (Sale.customer.contains(query))
        ).all()
        
        results['sales'] = [{
            'id': sale.id,
            'document_number': sale.document_number,
            'customer': sale.customer,
            'sale_date': sale.sale_date.strftime('%d.%m.%Y'),
            'total_amount': sale.total_amount
        } for sale in sales_results]
    
    if search_type in ['all', 'suppliers']:
        supplier_results = Supplier.query.filter(Supplier.name.contains(query)).all()
        
        results['suppliers'] = [{
            'id': supplier.id,
            'name': supplier.name,
            'contact_info': supplier.contact_info
        } for supplier in supplier_results]
    
    return jsonify(results)

# Обработчики ошибок
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error='Страница не найдена'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error='Внутренняя ошибка сервера'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)