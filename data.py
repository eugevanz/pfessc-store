import os

import pandas as pd
from bs4 import BeautifulSoup
from supabase import create_client, Client
from supafunc.errors import FunctionsRelayError, FunctionsHttpError

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
password: str = os.environ.get("SUPABASE_PASS")
supabase: Client = create_client(url, key)


class Pagination:
    def __init__(self, page, total_items):
        self.page = page
        self.per_page = 15
        self.total_items = total_items
        self.total_pages = (total_items // 15) + (1 if total_items % 15 > 0 else 0)

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def prev_num(self):
        return self.page - 1 if self.has_prev else None

    @property
    def has_next(self):
        return self.page < self.total_pages

    @property
    def next_num(self):
        return self.page + 1 if self.has_next else None

    def iter_pages(self, left_edge=2, left_current=2, right_current=2, right_edge=2):
        last = 0
        for num in range(1, self.total_pages + 1):
            pg__left_current = self.page - left_current - 1
            pg__right_current = self.page + right_current
            pg__right_edge = self.total_pages - right_edge
            if num <= left_edge or pg__left_current < num < pg__right_current or num > pg__right_edge:
                if last + 1 != num: yield None
                yield num
                last = num


def paginate_dataframe(df, page):
    total_items = len(df)
    per_page = 15
    total_pages = (total_items // per_page) + (1 if total_items % per_page > 0 else 0)

    if page < 1 or page > total_pages: return pd.DataFrame(), 0

    start = (page - 1) * per_page
    end = start + per_page
    paginated_df = df.iloc[start:end]

    return paginated_df, total_pages


def download_and_read_feather(bucket_name: str, source: str, destination: str):
    with open(destination, 'wb+') as f:
        res = supabase.storage.from_(bucket_name).download(source)
        f.write(res)
    return pd.read_feather(destination)


products_df = download_and_read_feather(
    bucket_name='public', source='Dataframes/products.feather', destination='products.feather')

collections_df = download_and_read_feather(
    bucket_name='public', source='Dataframes/collections.feather', destination='collections.feather')


def avail_sizes(variants: list) -> list:
    code_size_names = []
    for item in variants:
        if item["codeSizeName"]:
            code_size_names.append(item["codeSizeName"])
        code_size_names = list(set(code_size_names))
    return code_size_names


def avail_colours(variants: list) -> list:
    code_colour_names = []
    for item in variants:
        code_colour_names.append(item["codeColourName"])
        code_colour_names = list(set(code_colour_names))
    return code_colour_names


def colour_filter(colour: str) -> str:
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
               "DARK BLUE": "#00008B", "BROWN OLD": "#6E260E", "WHITE NAVY": "#B6D0E2", "BROWN": "#8B4513",
               "BLACK RED": "#FBFCFC", "Light Grey": "#d3d3d3", "NAVY NAVY": "#000080", "DARK RED": "#8B0000",
               "BLACK GREY": "#3F3F3F", "BLACK CYAN": "#008B8B", "BEIGE": "#FAF0E6", "BLACK WHITE": "#FAF9F6",
               "NAVY LIGHT BLUE": "#89CFF0", "BRIGHT GREEN": "#66FF00", "CAMOUFLAGE": "#78866B", "GREY LIME":
                   "#9DFD38", "GREEN GOLD": "#d8bb78", "BLACK ORANGE": "#FF8C00", "BLACK YELLOW": "#e1d816",
               "NATURAL BROWN": "#A27C5B"}
    return colours[colour]


def to_html_from_text(html_content: str):
    return BeautifulSoup(html_content, features="html.parser").get_text()


brands = supabase.table("Brands").select("code", "name", "image").execute()

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

default_img = "https://inyllwqsghzahwjosayv.supabase.co/storage/v1/object/public/Misc/branding-5_eba963a2-dc8f-47fe-b495-91101e675608.png?t=2024-05-07T06%3A14%3A55.152Z"
