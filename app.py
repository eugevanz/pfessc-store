import random
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from bs4 import BeautifulSoup
from data import categories, products, banners, default_img, sizes, collections, brands, genders, materials, fits, \
    keywords

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
templates.env.globals["categories_4"] = random.sample(categories.data, 4)
templates.env.filters["prettify_html"] = lambda html_content: BeautifulSoup(html_content,
                                                                            features="html.parser").get_text()

app.product_page = 0
app.selected_sizes, app.selected_genders, app.selected_materials, app.selected_fits = [], [], [], []
app.selected_brands, app.selected_keywords = [], []


def filter_store(selection_rem: str, selection_add: str, stored_filter: str):
    if selection_add is not None:
        if stored_filter == "size":
            app.selected_sizes.append(selection_add)
            app.selected_sizes = list(set(app.selected_sizes))
        elif stored_filter == "gender":
            app.selected_genders.append(selection_add)
            app.selected_genders = list(set(app.selected_genders))
        elif stored_filter == "material":
            app.selected_materials.append(selection_add)
            app.selected_materials = list(set(app.selected_materials))
        elif stored_filter == "fit":
            app.selected_fits.append(selection_add)
            app.selected_fits = list(set(app.selected_fits))
        elif stored_filter == "brand":
            app.selected_brands.append(selection_add)
            app.selected_brands = list(set(app.selected_brands))
        elif stored_filter == "keyword":
            app.selected_keywords.append(selection_add)
            app.selected_keywords = list(set(app.selected_keywords))
    if selection_rem is not None:
        try:
            if stored_filter == "size":
                app.selected_sizes.remove(selection_rem)
            elif stored_filter == "gender":
                app.selected_genders.remove(selection_rem)
            elif stored_filter == "material":
                app.selected_materials.remove(selection_rem)
            elif stored_filter == "fit":
                app.selected_fits.remove(selection_rem)
            elif stored_filter == "brand":
                app.selected_brands.remove(selection_rem)
            elif stored_filter == "keyword":
                app.selected_keywords.remove(selection_rem)
        except ValueError:
            print(f"The element '{selection_rem}' is not in the list")


def colour_filter(colour: str):
    if colour is None: return "#FFFAFA"
    colours = {"PINK": "#FF69B4", "RED": "#DC143C", "YELLOW": "#FFD700", "PURPLE": "#BA55D3",
               "STONE MILITARY GREEN": "#556B2F", "SKY BLUE": "#87CEEB", "DARK GREY": "#A9A9A9", "STONE": "#e3cba5",
               "ROYAL BLUE": "#4169E1", "BLUE": "#0000FF", "WHITE": "#FAF9F6", "GREY": "#808080", "NAVY": "#000080",
               "MILITARY GREEN": "#667C3E", "CHARCOAL": "#36454F", "BLACK": "#141414", "SOLID WHITE": "#FAF9F6",
               "NATURAL": "#FAF9F6", "GOLD": "#FFD700", "SILVER": "#C0C0C0", "GUN METAL": "#818589", "KHAKI": "#F0E68C",
               "TRANSPARENT": "#FAF9F6", "CYAN": "#7FFFD4", "LIME": "#32CD32", "GREEN": "#228B22", "ORANGE": "#FF7518",
               "TURQUOISE": "#40E0D0", "DARK GREEN": "#097969", "ROSE GOLD": "#E0BFB8", "BRONZE": "#CD7F32",
               "MAROON": "#800000", "AQUA": "#89CFF0", "OCEAN BLUE": "#0059b3", "CREAM": "#FFFDD0",
               "LIGHT BLUE": "#89CFF0", "WHITE BLACK": "#FAF9F6", "WHITE LIGHT BLUE": "#F0FFFF", "OLIVE": "#808000",
               "DARK BLUE": "#00008B", "BROWN OLD": "#6E260E", "WHITE NAVY": "#B6D0E2", "BROWN": "#8B4513"}
    return colours[colour]


templates.env.filters["colour_filter"] = colour_filter


def avail_colours(variants: list):
    code_colour_names = []
    for item in variants:
        code_colour_names.append(item["codeColourName"])
        code_colour_names = list(set(code_colour_names))
    return code_colour_names


templates.env.filters["avail_colours"] = avail_colours


def avail_sizes(variants: list):
    code_size_names = []
    for item in variants:
        if item["codeSizeName"]:
            code_size_names.append(item["codeSizeName"])
        code_size_names = list(set(code_size_names))
    return code_size_names


templates.env.filters["avail_sizes"] = avail_sizes


@app.get("/", response_class=HTMLResponse)
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


@app.get("/products-slider", response_class=HTMLResponse)
async def products_slider(request: Request):
    context = {
        "request": request,
        "banners": banners
    }
    return templates.TemplateResponse("products-slider.html", context=context)


@app.get("/products-grid", response_class=HTMLResponse)
async def products_grid(request: Request, page: int = None, is_feat: bool = False):
    if page is not None: app.product_page = max(page, 1)  # If page is provided, set product_page
    if app.product_page < 1:  app.product_page = 1  # Ensure product_page is always at least 1
    start = (app.product_page - 1) * 15  # Calculate the start index for pagination
    products_ = products.data  # Get products data
    context = {  # Prepare context data for template rendering
        "request": request,  # Request object
        "page": app.product_page,  # Current page number
        "default_img": default_img,  # Default image URL
        "is_feat": is_feat,  # Flag indicating if only featured products are requested
        "products": random.sample(products.data, 15) if is_feat else products_[start: (start + 15)]
    }
    return templates.TemplateResponse("products-grid.html", context=context)


@app.get("/product-filter", response_class=HTMLResponse)
async def product_filter(request: Request, a_size: str = None, r_size: str = None, a_gender: str = None,
                         r_gender: str = None, a_material: str = None, r_material: str = None, a_fit: str = None,
                         r_fit: str = None, a_brand: str = None, r_brand: str = None, a_keyword: str = None,
                         r_keyword: str = None):
    filter_store(r_size, a_size, "size")
    filter_store(r_gender, a_gender, "gender")
    filter_store(r_material, a_material, "material")
    filter_store(r_fit, a_fit, "fit")
    filter_store(r_brand, a_brand, "brand")
    filter_store(r_keyword, a_keyword, "keyword")
    context = {
        "request": request,
        "sizes": sizes,
        "selected_sizes": app.selected_sizes,
        "genders": genders,
        "selected_genders": app.selected_genders,
        "materials": materials,
        "selected_materials": app.selected_materials,
        "fits": fits,
        "selected_fits": app.selected_fits,
        "brands": [item["name"] for item in brands.data],
        "selected_brands": app.selected_brands,
        "keywords": keywords,
        "selected_keywords": app.selected_keywords
    }
    return templates.TemplateResponse("product-filter.html", context=context)


@app.get("/product-detail", response_class=HTMLResponse)
async def product_detail(request: Request, code: str):
    context = {
        "request": request,
        "product": next((product for product in products.data if product.get("fullCode") == code), None)
    }
    return templates.TemplateResponse("product-detail.html", context=context)


@app.get("/collections", response_class=HTMLResponse)
async def all_collections(request: Request):
    context = {
        "request": request
    }
    return templates.TemplateResponse("collections.html", context=context)


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


@app.get("/selected-pay-meth")
def selected_pay_meth(request: Request):
    return request.get("payment-method")


@app.get("/selected-billing-address")
def selected_billing_address(request: Request):
    return request.get("billing-addr")

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
