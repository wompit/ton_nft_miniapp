from datetime import datetime
from functools import wraps
from peewee import (
    Model,
    CharField,
    DateTimeField,
    IntegerField,
    ForeignKeyField,
    BooleanField,
)
from playhouse.postgres_ext import BinaryJSONField
from playhouse.pool import PooledPostgresqlExtDatabase

from config import DB_CONFIG

db = PooledPostgresqlExtDatabase(**DB_CONFIG)
db.commit_select = True
db.autorollback = True


def open_db_connection():
    if db.is_closed():
        db.connect()


def close_db_connection():
    if not db.is_closed():
        db.close()


def db_connect_wrapper(func):
    """
    connect to db and disconnect from it

    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            open_db_connection()
            return func(*args, **kwargs)
        finally:
            close_db_connection()

    return wrapper


class _Model(Model):
    class Meta:
        database = db


class User(_Model):
    class Meta:
        table_name = "users"

    telegram_id = CharField(unique=True, index=True, primary_key=False)
    name = CharField(index=True)
    date_of_birth = DateTimeField()
    race = CharField(max_length=50)
    planet = CharField(max_length=50)
    sex = CharField(max_length=50)
    position = CharField(max_length=50)
    wallet_address = CharField(unique=True, index=True)
    image_path = CharField(null=True)
    qr_code_path = CharField(null=True)
    created = DateTimeField(default=datetime.now)
    status = IntegerField(default=1)
    extra_data = BinaryJSONField(default={})

    def __repr__(self):
        return f"<NFTPassport {self.id}>"


class NFTPassport(_Model):
    class Meta:
        table_name = "nft_passports"

    user = ForeignKeyField(User)
    success = BooleanField(default=True)
    address = CharField(unique=True, index=True)
    mint_hash = CharField()
    metadata_hash = CharField()
    created = DateTimeField(default=datetime.now)


CREATING_LIST = [User, NFTPassport]


def init_db():
    try:
        db.connect()
        db.drop_tables(CREATING_LIST)
        print("tables dropped")
        db.create_tables(CREATING_LIST)
        print("tables created")
        db.close()
    except:
        db.rollback()
        raise
