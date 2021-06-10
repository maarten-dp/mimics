from mimics import Mimic
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def test_vanilla_celery(celery_app, celery_worker):
    # Vanilla celery test as found at
    # https://docs.celeryproject.org/en/stable/userguide/testing.html#fixtures
    @celery_app.task
    def mul(x, y):
        return x * y

    celery_worker.reload()

    assert mul.delay(4, 4).get(timeout=10) == 16


def test_mimicked_celery(celery_app, celery_worker):
    mimic = Mimic()
    celery_husk = mimic.husk()

    @celery_husk.task
    def mul(x, y):
        return x * y

    celery_app = mimic.absorb(celery_husk).as_being(celery_app)

    celery_worker.reload()

    assert mul.delay(4, 4).get(timeout=10) == 16


def test_it_can_mimic_flask_sqlalchemy():
    mimic = Mimic()
    husk = mimic.husk()

    class MyModel(husk.Model):
        id = husk.Column(husk.Integer, primary_key=True)
        name = husk.Column(husk.String(255), nullable=False, unique=True)

    husk.create_all()
    my_model = MyModel(name="test")
    husk.session.add(my_model)
    husk.session.commit()

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db = SQLAlchemy(app)

    mimic.absorb(husk).as_being(db)

    models = MyModel.query.all()
    assert len(models) == 1
    assert models[0].name == "test"
