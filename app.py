import os
import random

from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from data import banners, default_img, sizes, genders, materials, fits, \
    keywords, brands, categories, colour_filter, avail_colours, avail_sizes, to_html_from_text, products_df, \
    collections_df, paginate_dataframe, Pagination

database_uri = os.environ.get("DATABASE_URI")

app = Flask(__name__)

app.config["SECRET_KEY"] = "omniscient"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

db = SQLAlchemy(app=app)


class Product(db.Model):
    __tablename__ = "Products"
    simplecode = db.Column(db.String, primary_key=True)
    fullcode = db.Column(db.String)
    gender = db.Column(db.String)
    material = db.Column(db.String)
    fit = db.Column(db.String)
    description = db.Column(db.String)
    productname = db.Column(db.String)
    keywords = db.Column(db.ARRAY(db.String))
    islogo24 = db.Column(db.Boolean)
    brandname = db.Column(db.String)
    imagelist = db.Column(db.ARRAY(db.String))
    category = db.Column(db.String)
    codesizenames = db.Column(db.ARRAY(db.String))
    codecolournames = db.Column(db.ARRAY(db.String))
    price = db.Column(db.Float)


class Collections(db.Model):
    __tablename__ = "Collections"
    path = db.Column(db.String, primary_key=True)
    code = db.Column(db.String)
    image = db.Column(db.String)
    name = db.Column(db.String)


app.jinja_env.filters["prettify_html"] = to_html_from_text
app.jinja_env.filters["colour_filter"] = colour_filter
app.jinja_env.filters["avail_colours"] = avail_colours
app.jinja_env.filters["avail_sizes"] = avail_sizes


# def filter_products():
#     query = Product.query
#     for key, values in session.items():
#         if values and hasattr(Product, key):
#             column = getattr(Product, key)
#             if isinstance(values, list):
#                 if column.type.__class__.__name__ == 'ARRAY':
#                     like_filters = [column.any(func.lower(element)).like(f"%{value.lower()}%") for value in values]
#                 else:
#                     like_filters = [column.like(f"%{value}%") for value in values]
#                 query = query.filter(or_(*like_filters))
#             else:
#                 if column.type.__class__.__name__ == 'ARRAY':
#                     query = query.filter(column.any(func.lower(values)).like(f"%{values.lower()}%"))
#                 else:
#                     query = query.filter(column.like(f"%{values}%"))
#     return query


@app.context_processor
def inject_shared_data():
    return {"categories": random.sample(categories.data, 4)}


@app.route("/")
def index():
    products_ = products_df.sample(n=15).to_dict(orient='records')
    collections_ = collections_df.sample(n=15).to_dict(orient='records')
    return render_template(template_name_or_list="index.html", banners=banners, products=products_,
                           collections=collections_, brands=brands.data)


@app.route("/products/<int:page>/")
def all_products(page: int = 1):
    total_items = len(products_df)
    paginated_df, total_pages = paginate_dataframe(products_df, page)
    pagination_ = Pagination(page, len(products_df))
    products_ = paginated_df.to_dict(orient='records')
    return render_template("products.html", sizes=sizes, genders=genders, materials=materials,
                           fits=fits, brands=[item["name"] for item in brands.data], keywords=keywords,
                           products=products_, default_img=default_img, pagination=pagination_)


@app.route("/product-filter/")
def product_filter():
    session["gender"] = request.args.getlist("gender")
    session["size"] = request.args.getlist("size")
    session["material"] = request.args.getlist("material")
    session["fit"] = request.args.getlist("fit")
    session["brand"] = request.args.getlist("brand")
    session["keywords"] = request.args.getlist("keywords")

    return redirect(url_for("all_products", page=1))


@app.route("/products-slider/")
def products_slider():
    return render_template("products-slider.html", banners=banners)


@app.route("/products-grid/<int:page>", methods=['GET', 'POST'])
def products_grid():
    return render_template("products-grid.html")


# @app.route("/product-detail", methods=['GET', 'POST'])
# def product_detail():
#     form_data = request.form
#     product_data = form_data.get("product")
#     return render_template("product-detail.html", product=eval(product_data), recommended=random_products)


@app.route("/collections/")
def all_collections():
    return render_template("collections.html")


@app.route("/collections-grid/")
def collections_grid():
    collections_ = Collections.query.order_by(func.random()).all()
    return render_template("collections-grid.html", default_img=default_img, collections=collections_)


@app.route("/suppliers-grid/")
def suppliers_grid():
    return render_template("suppliers-grid.html", brands=brands.data)


# @app.route("/selected-pay-meth")
# def selected_pay_meth(request: Request):
#     return request.get("payment-method")


# @app.get("/selected-billing-address")
# def selected_billing_address(request: Request):
#     return request.get("billing-addr")


if __name__ == "__main__":
    app.run(debug=True)
