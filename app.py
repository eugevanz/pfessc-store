from flask import Flask, render_template, request
from supabase import create_client, Client
import os
import random

app = Flask(__name__)
app.jinja_env.globals.update(get_current_page_name=lambda: request.path.split("/")[1:])

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

products = supabase.table("Products").select("fullCode", "productName", "brand", "images", "variants", "keywords",
                                             "description").execute()
product_fullCodes = [product["fullCode"] for product in products.data]
prices = supabase.table("Prices").select("fullCode", "price").in_("fullCode", product_fullCodes).execute()

sizes = {}
for product in products.data:
    for variant in product["variants"]:
        code_size = variant["codeSize"]
        if code_size is not None:
            sizes[code_size] = sizes.get(code_size, 0) + 1


@app.context_processor
def utility_processor():
    menu_items = [
        {"url": "/", "label": "Home"},
        {"url": "/Shop All", "label": "Shop All"},
        {"url": "/Collections/LOGO-24", "label": "LOGO-24"},
        {"url": "/Collections/Mobile Tech", "label": "Mobile Tech"}
    ]
    sizes_ = dict(sorted(sizes.items()))
    return dict(menu_items=menu_items, prices=prices.data, sizes=sizes_)


@app.route("/selected-pay-meth")
def selected_pay_meth():
    return request.args.get("payment-method")


@app.route("/selected-billing-address")
def selected_billing_address():
    return request.args.get("billing-addr")


@app.route("/")
def home():
    featured = random.sample(products.data, 10)
    collections = [{"label": "Collection Name"}]
    return render_template("index.html", products=featured, collections=collections)


@app.route("/Shop All")
def shopall():
    page = request.args.get("page", 1, type=int)
    start_index = (page - 1) * 10
    paginated = supabase.table("Products").select("simpleCode", "productName", "brand", "images").range(start_index,
                                                                                                        start_index + 10).execute()
    return render_template("products.html", products=products.data, page=page)


@app.route("/Collections")
def all_collections():
    return render_template("collections.html")


@app.route("/add-to-cart/<item_id>")
def add_to_cart(item_id):
    item = dict({"name": item_id, "image": "product.image", "price": "product.price", "quantity": 1, "size": "L",
                 "color": "grey"})
    return render_template("cart-confirmation.html", product=item)


@app.route(rule="/buy-now", methods=["POST"])
def buy_now():
    item_name = request.form["name"]
    item_image = request.form["image"]
    item_price = request.form["price"]
    selected_quantity = int(request.form["quantity"])
    selected_size = request.form["size"]
    selected_color = request.form["color"]

    item = dict({"name": item_name, "image": item_image, "price": item_price, "quantity": selected_quantity,
                 "size": selected_size, "color": selected_color})
    return render_template("checkout.html", products=item)


@app.route("/product-detail/<item_id>")
def product_detail(item_id):
    product = products.data[0]
    return render_template("product-detail.html", product=product)


@app.route("/description/<fullCode>")
def item_desc(full_code: str):
    desc = next((product.get("description") for product in products.data if product.get("fullCode") == full_code), None)
    print(desc)
    return desc


if __name__ == "__main__":
    app.run(debug=True)
