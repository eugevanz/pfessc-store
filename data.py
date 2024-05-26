import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

products = supabase.table("Products").select(
    "fullCode", "productName", "brand", "images", "variants", "keywords", "description", "categories", "gender",
    "material", "fit"
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

genders, materials, fits, keywords = [], [], [], []
for product in products.data:
    if product["gender"] is not None:
        genders.append(product["gender"])
        genders = list(set(genders))
    if product["material"] != "":
        materials.append(product["material"])
        materials = list(set(materials))
    if product["fit"] != "":
        fits.append(product["fit"])
        fits = list(set(fits))
    if product["keywords"] != "NULL" or product["keywords"] != "":
        parts = product["keywords"].split(';')
        for part in parts:
            keywords.extend(part.split(","))
        keywords = list(set(keywords))
        keywords = [item for item in keywords if item.strip()]

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
