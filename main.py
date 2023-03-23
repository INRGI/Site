from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user
from wtforms_alchemy import ModelForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from models import db
from models import Category, Item
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_session import Session
from dotenv import load_dotenv
from servises import Cart, Adons
import os

from flask_admin.form import ImageUploadField

class ItemView(ModelView):
    column_list = ('name', 'description', 'price', 'categorys', 'image')
    form_columns = ('name', 'description', 'price', 'categorys', 'image')
    form_extra_fields = {
        'image': ImageUploadField('Image',
            base_path=os.path.join(os.path.dirname(__file__), 'static/img'),
            url_relative_path='img/')
    }

class CategoryView(ModelView):
    column_list = ('title', 'image')
    form_columns = ('title', 'image')
    form_extra_fields = {
        'image': ImageUploadField('Image',
            base_path=os.path.join(os.path.dirname(__file__), 'static/img'),
            url_relative_path='img/')
    }

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DB"]
app.config['FLASK_ADMIN_SWATCH'] = os.environ["ADMIN_THEME"]
app.secret_key = os.environ["SECRET_KEY"]
app.config['SESSION_TYPE'] = os.environ["SESSION_TYPE"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String)

sess = Session()
sess.init_app(app)

db.init_app(app)
with app.app_context():
    db.create_all()

admin = Admin(app, name
              ='NRG/SHOP', template_mode='bootstrap3')
admin.add_view(CategoryView(Category, db.session))
admin.add_view(ItemView(Item, db.session))

@app.route('/')
@login_required
def index():
    categorys = Category.query.all()
    return render_template('index.html', categorys=categorys)

@app.route('/category/<int:category_id>')
def get_category(category_id):
    category = Category.query.filter(Category.id == category_id).first()
    return render_template('items.html',category=category)

@app.route('/item/<int:item_id>')
def one_item(item_id):
    item = Item.query.filter(Item.id == item_id).first()
    return render_template('item.html',item=item)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_id = request.form.get('item_id')
    item = Adons.get_item_by_id(item_id)
    cart = session.get('cart', Cart())
    cart.add_item(item)
    session['cart'] = cart
    return redirect(url_for('cart'))


@app.route('/delete_from_cart', methods=['POST'])
def delete_from_cart():
    item_id = request.form.get('item_id')
    try:
        item_id = int(item_id)
        session["cart"].remove_item(item_id)
    except Exception:
        pass
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart = session.get('cart', Cart())
    return render_template('cart.html', cart=cart)



login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

class UserForm(ModelForm):
    class Meta:
        model = User

class UserRegistrationForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=30)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_login(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user is not None:
            raise ValidationError('Please use a different login.')

@app.route('/register', methods=["POST","GET"])
def register():
    form = UserRegistrationForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = User(login=form.login.data, password=generate_password_hash(form.password.data))
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect('/')
    return render_template('registration.html', form=form)

@app.route('/login', methods=["POST","GET"])
def login():
    form = UserForm()
    if request.method == "POST":
        form_data = request.form
        user =User.query\
               .filter(User.login == form_data.get("login"))\
               .filter(User.password == form_data.get("password"))\
               .first()
        if user and check_password_hash(user.password, form_data.get("password")):
            login_user(user)
            return redirect('/')
    return render_template('login.html', form=form)


if __name__ == '__main__':
    app.run()

