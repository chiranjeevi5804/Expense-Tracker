
from app import create_app
from models import db, Category, Expense, Budget


def test_app_and_db():
    app = create_app()

    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })

    with app.app_context():
        db.create_all()

        category = Category(name='Test Category')
        db.session.add(category)
        db.session.commit()

        expense = Expense(
            description='Test expense',
            amount=100,
            category_id=category.id
        )

        db.session.add(expense)
        db.session.commit()

        assert Expense.query.count() == 1
        assert Category.query.count() == 1

        expense.amount = 150
        db.session.commit()

        assert Expense.query.first().amount == 150

        db.session.delete(expense)
        db.session.commit()

        assert Expense.query.count() == 0

        db.drop_all()
