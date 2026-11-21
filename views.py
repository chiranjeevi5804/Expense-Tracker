
from flask import Blueprint, request, jsonify, render_template, Response
from models import db, Expense, Category, Budget
from sqlalchemy import func
from datetime import datetime
import csv
import io
import math
import re

main_bp = Blueprint('main', __name__)


def valid_month(month):
    if not isinstance(month, str) or not re.fullmatch(r'\d{4}-\d{2}', month):
        return False
    try:
        datetime.strptime(month, '%Y-%m')
        return True
    except ValueError:
        return False


def error(message, status=400):
    return jsonify({'error': message}), status


@main_bp.route('/')
def index():
    return render_template('index.html')


# ---------------- CATEGORIES ----------------

@main_bp.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        name = data.get('name', '')

        if not isinstance(name, str):
            return error('Invalid category name')

        name = name.strip()

        if not name or len(name) > 80:
            return error('Category name must contain 1 to 80 characters')

        existing = Category.query.filter(
            func.lower(Category.name) == name.lower()
        ).first()

        if existing:
            return error('This category already exists', 409)

        category = Category(name=name)
        db.session.add(category)
        db.session.commit()

        return jsonify({
            'id': category.id,
            'name': category.name
        }), 201

    records = Category.query.order_by(Category.name).all()

    return jsonify([
        {'id': c.id, 'name': c.name}
        for c in records
    ])


@main_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = db.session.get(Category, category_id)
    if category is None:
        return error('Category not found', 404)
    if Expense.query.filter_by(category_id=category_id).first() or Budget.query.filter_by(category_id=category_id).first():
        return error('This category is in use. Remove its expenses and budgets before deleting it.', 409)
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully'})


# ---------------- EXPENSES ----------------

@main_bp.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}

        try:
            amount = float(data.get('amount', 0))
            category_id = int(data.get('category_id', 0))
        except (ValueError, TypeError):
            return error('Enter a valid amount and category')

        description = data.get('description', '')

        if not isinstance(description, str):
            return error('Invalid description')

        description = description.strip()

        if not math.isfinite(amount) or amount <= 0:
            return error('Amount must be greater than zero')

        if len(description) > 200:
            return error('Description cannot exceed 200 characters')

        category = db.session.get(Category, category_id)

        if not category:
            return error('Selected category does not exist')

        expense = Expense(
            description=description,
            amount=amount,
            category_id=category_id
        )

        db.session.add(expense)
        db.session.commit()

        return jsonify({
            'message': 'Expense added successfully',
            'id': expense.id
        }), 201

    month = request.args.get('month')

    query = Expense.query

    if month:
        if not valid_month(month):
            return error('Month must be in YYYY-MM format')

        query = query.filter(
            func.strftime('%Y-%m', Expense.created_at) == month
        )

    records = query.order_by(
        Expense.created_at.desc()
    ).all()

    return jsonify([
        {
            'id': e.id,
            'description': e.description or '',
            'amount': e.amount,
            'category_id': e.category_id,
            'category': e.category.name if e.category else 'Unknown',
            'created_at': e.created_at.isoformat()
        }
        for e in records
    ])


@main_bp.route('/expenses/<int:expense_id>', methods=['PUT', 'DELETE'])
def manage_expense(expense_id):
    expense = db.session.get(Expense, expense_id)

    if not expense:
        return error('Expense not found', 404)

    if request.method == 'DELETE':
        db.session.delete(expense)
        db.session.commit()

        return jsonify({'message': 'Expense deleted successfully'})

    data = request.get_json(silent=True) or {}

    if 'amount' in data:
        try:
            amount = float(data['amount'])
        except (ValueError, TypeError):
            return error('Enter a valid amount')

        if not math.isfinite(amount) or amount <= 0:
            return error('Amount must be greater than zero')

        expense.amount = amount

    if 'description' in data:
        description = data['description']

        if not isinstance(description, str) or len(description.strip()) > 200:
            return error('Description cannot exceed 200 characters')

        expense.description = description.strip()

    if 'category_id' in data:
        try:
            category_id = int(data['category_id'])
        except (ValueError, TypeError):
            return error('Invalid category')

        if not db.session.get(Category, category_id):
            return error('Selected category does not exist')

        expense.category_id = category_id

    db.session.commit()

    return jsonify({'message': 'Expense updated successfully'})


# ---------------- BUDGETS ----------------

@main_bp.route('/budgets', methods=['GET', 'POST'])
def budgets():
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}

        try:
            category_id = int(data.get('category_id', 0))
            amount = float(data.get('amount', 0))
        except (ValueError, TypeError):
            return error('Enter valid budget details')

        month = data.get('month')

        if not valid_month(month):
            return error('Month must be in YYYY-MM format')

        if not math.isfinite(amount) or amount <= 0:
            return error('Budget must be greater than zero')

        if not db.session.get(Category, category_id):
            return error('Selected category does not exist')

        budget = Budget.query.filter_by(
            category_id=category_id,
            month=month
        ).first()

        if budget:
            budget.amount = amount
        else:
            budget = Budget(
                category_id=category_id,
                month=month,
                amount=amount
            )
            db.session.add(budget)

        db.session.commit()

        return jsonify({
            'message': 'Budget saved successfully',
            'id': budget.id
        }), 201

    records = Budget.query.order_by(
        Budget.month.desc()
    ).all()

    return jsonify([
        {
            'id': b.id,
            'category_id': b.category_id,
            'category': b.category.name if b.category else 'Unknown',
            'month': b.month,
            'amount': b.amount
        }
        for b in records
    ])


@main_bp.route('/budgets/<int:budget_id>', methods=['PUT', 'DELETE'])
def manage_budget(budget_id):
    budget = db.session.get(Budget, budget_id)
    if budget is None:
        return error('Budget not found', 404)
    if request.method == 'DELETE':
        db.session.delete(budget)
        db.session.commit()
        return jsonify({'message': 'Budget deleted successfully'})
    data = request.get_json(silent=True) or {}
    try:
        amount = float(data.get('amount'))
    except (ValueError, TypeError):
        return error('Enter a valid budget amount')
    if not math.isfinite(amount) or amount <= 0:
        return error('Budget must be greater than zero')
    budget.amount = amount
    db.session.commit()
    return jsonify({'message': 'Budget updated successfully'})


# ---------------- MONTHLY REPORT ----------------

@main_bp.route('/reports/monthly', methods=['GET'])
def monthly_report():
    month = request.args.get('month', '')

    if not valid_month(month):
        return error('Provide a valid month in YYYY-MM format')

    categories_list = Category.query.order_by(Category.name).all()
    result = []

    for category in categories_list:
        spent = db.session.query(
            func.sum(Expense.amount)
        ).filter(
            Expense.category_id == category.id,
            func.strftime('%Y-%m', Expense.created_at) == month
        ).scalar() or 0

        budget = Budget.query.filter_by(
            category_id=category.id,
            month=month
        ).first()

        budget_amount = budget.amount if budget else None

        result.append({
            'category_id': category.id,
            'category': category.name,
            'spent': float(spent),
            'budget': budget_amount,
            'remaining': (
                float(budget_amount - spent)
                if budget_amount is not None else None
            ),
            'within_budget': (
                budget_amount is None or spent <= budget_amount
            )
        })

    return jsonify(result)


# ---------------- CSV EXPORT ----------------

@main_bp.route('/reports/monthly.csv', methods=['GET'])
def download_monthly_report():
    month = request.args.get('month', '')

    if not valid_month(month):
        return error('Provide a valid month in YYYY-MM format')

    report = monthly_report_data(month)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Month',
        'Category',
        'Total Spent',
        'Budget',
        'Remaining',
        'Status'
    ])

    for item in report:
        writer.writerow([
            month,
            item['category'],
            item['spent'],
            item['budget'] if item['budget'] is not None else 'Not set',
            item['remaining'] if item['remaining'] is not None else 'Not set',
            'Within Budget' if item['within_budget'] else 'Budget Exceeded'
        ])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition':
                f'attachment; filename=expense-report-{month}.csv'
        }
    )


def monthly_report_data(month):
    categories_list = Category.query.order_by(Category.name).all()
    result = []

    for category in categories_list:
        spent = db.session.query(
            func.sum(Expense.amount)
        ).filter(
            Expense.category_id == category.id,
            func.strftime('%Y-%m', Expense.created_at) == month
        ).scalar() or 0

        budget = Budget.query.filter_by(
            category_id=category.id,
            month=month
        ).first()

        budget_amount = budget.amount if budget else None

        result.append({
            'category': category.name,
            'spent': float(spent),
            'budget': budget_amount,
            'remaining': (
                float(budget_amount - spent)
                if budget_amount is not None else None
            ),
            'within_budget': (
                budget_amount is None or spent <= budget_amount
            )
        })

    return result
