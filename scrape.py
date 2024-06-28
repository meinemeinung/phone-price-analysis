import itertools
import requests
from bs4 import BeautifulSoup
import pandas as pd

def parse_phone_specification(html: str):
    spec = {}
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find(id="Spesifikasi").find("table")
    price = soup.find("a", {"class":"filter-button lowest-price-detail"})
    if price:
        spec['price'] = price.text.strip()
    spec_key = table.find_all("td", {"class":"spec-key"})
    spec_value = table.find_all("td", {"class":"spec-value"})

    if len(spec_key) != len(spec_value):
        raise ValueError("Key and val have different length!")
    else:
        n = len(spec_key)
        for i in range(n):
            key = spec_key[i].text.strip()
            val = spec_value[i].text.strip()
            spec[key] = val

    return spec

if __name__=='__main__':
    brands = ['OPPO', 'Samsung', 'Apple', 'Realme', 'Vivo', 'Xiaomi', 'Infinix', 'Nokia']
    num_pages = 100
    url = "https://portal.pricebook.co.id/pb/category/product?category_id=40"
    all_spec = []

    for num_page, brand in itertools.product(range(1, num_pages), brands):
        print(f'Brand {brand} page {num_page}')
        brand_page_url = f"{url}&brand={brand}&page={num_page}"
        r = requests.get(brand_page_url)
        response = r.json()
        for product in list(response['result']['product']):
            product_url = product['url']
            product_request = requests.get(product_url)
            spec = parse_phone_specification(product_request.text)
            all_spec.append(spec)

    all_spec = pd.DataFrame.from_records(all_spec)
    all_spec.to_csv('phone_data.csv')