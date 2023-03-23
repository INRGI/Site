from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()



class Category(db.Model):
    __tablename__ = "category_table"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    items = db.relationship("Item", back_populates="categorys")
    image = db.Column(db.String(255))
    def __str__(self):
        return self.title

class Item(db.Model):
    __tablename__ = "item_table"
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category_table.id"))
    categorys = db.relationship("Category", back_populates="items")
    name = db.Column(db.String(50))
    description = db.Column(db.String)
    price = db.Column(db.Integer)
    image = db.Column(db.String(255))
    
    def __str__(self):
        return self.name


