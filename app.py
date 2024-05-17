import os
import random

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.product_page = 0

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

products = supabase.table("Products").select(
    "fullCode", "productName", "brand", "images", "variants", "keywords", "description", "categories"
).execute()
brands = supabase.table("Brands").select("code", "name", "image").execute()
product_fullCodes = [product["fullCode"] for product in products.data]
prices = supabase.table("Prices").select("fullCode", "price").in_("fullCode", product_fullCodes).execute()
price_lookup = {price["fullCode"]: price["price"] for price in prices.data}
for product in products.data:
    full_code = product["fullCode"]
    if full_code in price_lookup:
        product["price"] = price_lookup[full_code]
banners = [
    "https://inyllwqsghzahwjosayv.supabase.co/storage/v1/object/public/Banners/PFESSC%20Banners.001.png",
    "https://inyllwqsghzahwjosayv.supabase.co/storage/v1/object/public/Banners/PFESSC%20Banners.002.png",
    "https://inyllwqsghzahwjosayv.supabase.co/storage/v1/object/public/Banners/PFESSC%20Banners.003.png",
    "https://inyllwqsghzahwjosayv.supabase.co/storage/v1/object/public/Banners/PFESSC%20Banners.004.png",
    "https://inyllwqsghzahwjosayv.supabase.co/storage/v1/object/public/Banners/PFESSC%20Banners.005.png"
]
categories = supabase.table("Categories").select("categoryCode", "categoryName", "children").execute()

sizes = {}
for product in products.data:
    for variant in product["variants"]:
        code_size = variant["codeSize"]
        if code_size is not None:
            sizes[code_size] = sizes.get(code_size, 0) + 1

collections = set()
for product in products.data:
    for category in product["categories"]:
        collections.add((category["code"], category["name"], category["path"], category["image"]))
collections = [{"code": code, "name": name, "path": path, "image": image} for code, name, path, image in collections]

default_img = "https://inyllwqsghzahwjosayv.supabase.co/storage/v1/object/public/Misc/branding-5_eba963a2-dc8f-47fe-b495-91101e675608.png?t=2024-05-07T06%3A14%3A55.152Z"


@app.get("/", response_class=HTMLResponse)
async def base(request: Request):
    context = {
        "request": request,
        "categories": categories.data,
        "categories_4": random.sample(categories.data, 4),
        "products": products.data
    }
    return templates.TemplateResponse("base.html", context=context)


@app.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    context = {
        "request": request,
        "banners": banners
    }
    return templates.TemplateResponse("index.html", context=context)


@app.get("/products", response_class=HTMLResponse)
async def all_products(request: Request):
    context = {
        "request": request
    }
    return templates.TemplateResponse("products.html", context=context)


@app.get("/collections", response_class=HTMLResponse)
async def all_collections(request: Request):
    context = {
        "request": request
    }
    return templates.TemplateResponse("collections.html", context=context)


@app.get("/products-slider", response_class=HTMLResponse)
async def products_slider(request: Request):
    context = {
        "request": request,
        "banners": banners
    }
    return templates.TemplateResponse("products-slider.html", context=context)


@app.get("/products-grid", response_class=HTMLResponse)
async def products_grid(request: Request, page: int = None, is_feat: bool = False):
    # Ensure page is always greater than or equal to 1
    if page is not None: app.product_page = max(page, 1)  # If page is provided, set product_page
    # to the maximum of page or 1
    if app.product_page < 1:  app.product_page = 1  # Ensure product_page is always at least 1

    # Calculate the start index for pagination
    start = (app.product_page - 1) * 15

    # Get products data
    products_ = products.data

    # Prepare context data for template rendering
    context = {
        "request": request,  # Request object
        "page": app.product_page,  # Current page number
        "default_img": default_img,  # Default image URL
        "is_feat": is_feat,  # Flag indicating if only featured products are requested
        # Select products based on is_feat flag: either a random sample of 15
        # products or a subset starting from start index
        "products": random.sample(products.data, 15) if is_feat else products_[start: (start + 15)]
    }

    # Render the HTML template with the context data
    return templates.TemplateResponse("products-grid.html", context=context)


@app.get("/collections-grid", response_class=HTMLResponse)
async def collections_grid(request: Request, is_feat: bool = False):
    context = {
        "request": request,
        "default_img": default_img,
        "collections": random.sample(collections, 15) if is_feat else collections
    }
    return templates.TemplateResponse("collections-grid.html", context=context)


@app.get("/suppliers-grid", response_class=HTMLResponse)
async def suppliers_grid(request: Request):
    context = {
        "request": request,
        "brands": brands.data
    }
    return templates.TemplateResponse("suppliers-grid.html", context=context)


@app.get("/product-filter", response_class=HTMLResponse)
async def product_filter(request: Request):
    context = {
        "request": request
    }
    return templates.TemplateResponse("product-filter.html", context=context)


@app.get("/selected-pay-meth")
def selected_pay_meth(request: Request):
    return request.get("payment-method")


@app.get("/selected-billing-address")
def selected_billing_address(request: Request):
    return request.get("billing-addr")

# @app.route("/Collections")
# def all_collections():
#     return render_template("collections.html")


# @app.route("/add-to-cart/<item_id>")
# def add_to_cart(item_id):
#     item = dict({"name": item_id, "image": "product.image", "price": "product.price", "quantity": 1, "size": "L",
#                  "color": "grey"})
#     return render_template("cart-confirmation.html", product=item)


# @app.route(rule="/buy-now", methods=["POST"])
# def buy_now():
#     item_name = request.form["name"]
#     item_image = request.form["image"]
#     item_price = request.form["price"]
#     selected_quantity = int(request.form["quantity"])
#     selected_size = request.form["size"]
#     selected_color = request.form["color"]
#
#     item = dict({"name": item_name, "image": item_image, "price": item_price, "quantity": selected_quantity,
#                  "size": selected_size, "color": selected_color})
#     return render_template("checkout.html", products=item)


# @app.route("/product-detail/<item_id>")
# def product_detail(item_id):
#     product = products.data[0]
#     return render_template("product-detail.html", product=product)


# @app.route("/description/<fullCode>")
# def item_desc(full_code: str):
#     desc = next((product.get("description") for product in products.data if product.get("fullCode") == full_code), None)
#     print(desc)
#     return desc


# if __name__ == "__main__":
#     app.run(debug=True)
