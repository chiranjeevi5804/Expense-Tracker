import click
from flask.cli import with_appcontext
from models import db, Category


@click.command('db-init')
@with_appcontext
def init_db_cmd():
    db.create_all()

    default_categories = [
        'Food',
        'Transport',
        'Entertainment',
        'Others'
    ]

    for name in default_categories:
        category = Category.query.filter_by(name=name).first()

        if not category:
            db.session.add(Category(name=name))

    db.session.commit()

    click.echo('Database initialized successfully!')
    click.echo('Default categories added successfully!')
