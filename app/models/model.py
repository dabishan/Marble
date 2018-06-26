from pymongo import MongoClient
from bson.objectid import ObjectId
from app.app import app

from app.models.structure import Structure, State


class Database:
    """ Parent Model class to give interface to other models"""
    @classmethod
    def __init__(cls, db):
        """ Initialize pymongo db instance"""
        with app.app_context():
            client = MongoClient(app.config['MONGODB_HOST'], app.config['MONGODB_PORT'])

        cls.db = client[db]


class Collection:
    # TODO : Simplify class. This class may not be necessary if wrote properly

    def __init__(self, db_name=None):
        with app.app_context():
            self._db = Database(app.config['DEFAULT_DB'] if db_name is None else db_name).db

    def get(self, collection):
        return self._db[collection]


class Model(Structure):
    """ Creates interface to pymongo collection and addition CRUD functions """
    collection_name = None
    _state = State.NEW

    def __init__(self, **kwargs):
        if self.collection_name is None:
            raise ValueError("collection_name not defined for Model")
        self.collection = Collection().get(self.collection_name)
        super(Model, self).__init__(**kwargs)
        self.id = ObjectId()
        self._state = State.NEW
    
    def load(self, item_id, required=True):
        """ Get item using an existing item id. Has to be present in db, unless required set to False"""
        self.id = item_id
        if item_id is None or item_id is False:
            raise ValueError("Id property of item is None or False")
        try:
            items = self.collection.find_one({'_id': item_id})
        except Exception:
            raise self.__db_error()
        if items is None and required:
            raise IndexError("Cannot find an item with given id")
        self._state = State.SAVED
        for key in items.keys():
            self[key] = items[key]
        return self

    def remove(self):
        if self._state == State.DELETED or self._state == State.NEW:
            raise ValueError("Tried to delete unsaved or deleted item")

        try:
            self.collection.delete_one({'_id': self.id})
            self._state = State.DELETED
        except Exception:
            raise self.__db_error()

    def save(self):
        if self._state == State.DELETED:
            raise ValueError("Tried to save deleted item")
        self.validate()

        self.collection.update_one({'_id': self.id}, {'$set': self}, upsert=True)
        return True

    @classmethod
    def __db_error(cls):
        return ConnectionError("Cannot connect to the database")
