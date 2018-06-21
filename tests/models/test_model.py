import pytest
from bson import ObjectId
from app.app import app
from app.models.model import Collection
from app.models.model import Model


def test_model_definition():
    with pytest.raises(ValueError, message="Allowed to create model without collection_name"):
        class Item(Model):
            pass
        Item().load(ObjectId())


test_collection = 'items'


class Item(Model):
    collection_name = test_collection


class TestModel:
    @pytest.fixture(scope="module")
    def setup(app_setup):
        test_id = ObjectId()
        app.config['DEFAULT_DB'] = test_collection
        app.logger.debug("This is a debug message")
        collection = Collection().get('items')
        collection.insert_many([
            {'_id': test_id, 'name': 'Product1', 'price': 5},
            {'_id': ObjectId(), 'name': 'Product2', 'price': 10}
        ])
        yield dict(collection=collection, test_id=test_id)
        collection.drop()

    def test_add(self, setup):
        product = Item(name='Product3', price=15, enabled=True)
        product.update(price=25, stock=300)
        product.save()

        product_from_db = setup['collection'].find_one({'_id': product.id})
        assert product_from_db is not None, "Test Error. Returned None instead of an item"
        assert product_from_db['price'] == 25 , "add_properties did not update instance"
        assert product_from_db['stock'] == 300, "app_properties did not add new field"

    def test_find(self, setup):
        with pytest.raises(IndexError, message="Did not raise IndexError on item id not in db"):
            Item().load(ObjectId())

        product = Item().load(setup['test_id'])
        assert product is not None, "Returned None instead of an item"
        assert product['name'] == 'Product1'

    def test_update(self, setup):
        product = Item().load(setup['test_id'])
        product['stock'] = 500
        product['price'] = 29
        product.save()

        product_from_db = setup['collection'].find_one({'_id': setup['test_id']})
        assert product_from_db is not None, "Test Error. Returned None instead of an item"
        assert product_from_db['price'] == 29, "add_properties did not update instance"
        assert product_from_db['stock'] == 500, "app_properties did not add new field"

    def test_remove(self, setup):
        product = Item(name="Product5", price=18)
        with pytest.raises(ValueError, message="Allowed removing new item"):
            product.remove()

        product = Item().load(setup['test_id'])
        product.remove()

        product_from_db = setup['collection'].find_one({'_id': product.id})
        assert product_from_db is None, "Item didn't get deleted from db"

        with pytest.raises(ValueError, message="Allowed modified fields of deleted item"):
            product['price'] = 20

        with pytest.raises(ValueError, message="Allowed removing item already deleted"):
            product.remove()

