import pytest
from bson import ObjectId
from app.models.model import Collection, Structure
from app.models.model import Model
from tests.models.fixtures import app_setup


def test_model_definition():
    with pytest.raises(ValueError, message="Allowed to create model without collection_name"):
        class Item(Model):
            pass
        Item().load(ObjectId())


test_collection = 'items'


class EmbeddedItem(Structure):
    fields = dict(
        name=dict(required=True, type=str),
        value=dict(required=False, type=int)
    )


class Item(Model):
    collection_name = test_collection
    fields = dict(
        name=dict(required=True, type=str),
        price=dict(type=float),
        address=dict(type=EmbeddedItem)
    )


class TestModel:
    @pytest.fixture(scope="module")
    def setup(self, app_setup):
        test_id = ObjectId()
        collection = Collection().get('items')
        collection.insert_many([
            {'_id': test_id, 'name': 'Product1', 'price': 5.0},
            {'_id': ObjectId(), 'name': 'Product2', 'price': 10.0}
        ])
        yield dict(collection=collection, test_id=test_id)
        # collection.drop()

    def test_add(self, setup):
        product = Item(name='Product3', price=15.0, enabled=True)
        product.update(price=25.0, stock=300)
        product.save()

        product_from_db = setup['collection'].find_one({'_id': product.id})
        assert product_from_db is not None, "Test Error. Returned None instead of an item"
        assert product_from_db['price'] == 25.0, "add_properties did not update instance"
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
        product['price'] = 29.0
        product.save()

        product_from_db = setup['collection'].find_one({'_id': setup['test_id']})
        assert product_from_db is not None, "Test Error. Returned None instead of an item"
        assert product_from_db['price'] == 29.0, "add_properties did not update instance"
        assert product_from_db['stock'] == 500, "app_properties did not add new field"

    def test_remove(self, setup):
        product = Item(name="Product5", price=18.0)
        with pytest.raises(ValueError, message="Allowed removing new item"):
            product.remove()
        product_to_delete = setup['collection'].insert_one({'name': 'Product1', 'price': 5.0})
        product = Item().load(product_to_delete.inserted_id)
        product.remove()

        product_from_db = setup['collection'].find_one({'_id': product.id})
        assert product_from_db is None, "Item didn't get deleted from db"

        with pytest.raises(ValueError, message="Allowed modified fields of deleted item"):
            product['price'] = 20.0

        with pytest.raises(ValueError, message="Allowed removing item already deleted"):
            product.remove()

    def test_validation(self, setup):
        product = Item()
        with pytest.raises(ValueError, message="Allowed adding field without meeting type validation"):
            product['price'] = "5"

        product['price'] = 5.0
        with pytest.raises(ValueError, message="Allowed saving without meeting requirement validation"):
            product.save()

        with pytest.raises(ValueError, message="Allowed saving without meeting type validation of Structure"):
            product['address'] = EmbeddedItem(name=15)
            product['address']['value'] = "name"

        with pytest.raises(ValueError, message="Allowed saving without meeting validation"):
            product.save()

    def test_save_with_structure(self, setup):
        product = Item(name="Product85")
        product['price'] = 29.0
        product['address'] = EmbeddedItem()
        product['address']['name'] = "Embedded1"
        product.save()
        product_from_db = setup['collection'].find_one({'_id': product.id})
        assert product_from_db['address'] is not None, "Didn't save embedded structure"
        assert product_from_db['address']['name'] == "Embedded1", "Didn't save field of embedded structure"

    def test_save_structure_with_load(self, setup):
        product = Item().load(setup['test_id'])
        product['address'] = EmbeddedItem(name="name")
        product['address']['name'] = "Embedded1"
        product.save()

        product_from_db = setup['collection'].find_one({'_id': setup['test_id']})
        assert product_from_db['address']['name'] == "Embedded1", "Didn't update field of embedded structure"

    def test_save_multi_structure(self, setup):
        product = Item(name="Product86")
        product['address'] = EmbeddedItem(name="asdf")

        product['address']['default'] = EmbeddedItem()
        with pytest.raises(ValueError, message="Allowed multi-level embed without meeting validation"):
            product['address']['default'] = EmbeddedItem(value="string")
            product['address']['default'] = EmbeddedItem(value=8)

        with pytest.raises(ValueError, message="Allowed saving with multi-level embed without meeting validation"):
            product.save()

        product['address']['default']['name'] = "Default"
        product.save()
        product_from_db = setup['collection'].find_one({'_id': product.id})

        assert 'default' in product_from_db['address'], "Didn't save embedded structure"


class TestStructure:
    def test_validation(self):
        with pytest.raises(ValueError, message="Allowed saving without meeting requirement of Embed validation"):
            em = EmbeddedItem(name=8)

        em = EmbeddedItem()
        with pytest.raises(ValueError, message="Allowed saving without meeting requirement of Embed validation"):
            em['name'] = 5
            em['value'] = "asd"

