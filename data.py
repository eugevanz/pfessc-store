import os

from supabase import create_client, Client
from supafunc.errors import FunctionsRelayError, FunctionsHttpError

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

random_products = supabase.table("random_products").select("*").limit(15).execute()

selected_product = lambda code: supabase.table("Products").select(
    "fullCode", "productName", "brand", "images", "variants", "keywords", "description", "categories", "gender",
    "material", "fit"
).eq("fullCode", code).execute()

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

try:
    genders = [r for r in supabase.rpc("get_distinct_genders").execute().data if r]
    materials = [r for r in supabase.rpc("get_distinct_materials").execute().data if r]
    fits = [r for r in supabase.rpc("get_distinct_fits").execute().data if r]
    keywords = [r["keyword"] for r in supabase.rpc("get_distinct_keywords").execute().data if r]
    sizes = [r for r in supabase.rpc("get_distinct_sizes").execute().data if r]
except (FunctionsRelayError, FunctionsHttpError) as exception:
    err = exception.to_dict()
    print(err.get("message"))

collections = set()
for product in products.data:
    for category in product["categories"]:
        collections.add((category["code"], category["name"], category["path"], category["image"]))
collections = [{"code": code, "name": name, "path": path, "image": image} for code, name, path, image in collections]

default_img = "https://inyllwqsghzahwjosayv.supabase.co/storage/v1/object/public/Misc/branding-5_eba963a2-dc8f-47fe-b495-91101e675608.png?t=2024-05-07T06%3A14%3A55.152Z"
