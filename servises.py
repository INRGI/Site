from models import Item

class Cart:
    def __init__(self):
        self.items = []
    def add_item(self, item):
        self.items.append(item)
    def get_price(self):
        price = 0
        for item in self.items:
            price += item.price
        return price
    def remove_item(self, item_id):
        self.items = [item for item in self.items if item.id != item_id]
    def get_items(self):
        return self.items

class Adons():
    def get_item_by_id(item_id):
        return Item.query.filter(Item.id == item_id).first()

