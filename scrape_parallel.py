import itertools
import multiprocessing as mp
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
        for key, val in zip(spec_key, spec_value):
            spec[key.text.strip()] = val.text.strip()

    return spec

def fetch_brand_page_spec(brand, num_page):
    url = "https://portal.pricebook.co.id/pb/category/product?category_id=40"
    r = requests.get(url, params={'brand':brand, 'page':num_page})
    response = r.json()
    page_spec = []
    for product in list(response['result']['product']):
        product_url = product['url']
        product_request = requests.get(product_url)
        spec = parse_phone_specification(product_request.text)
        page_spec.append(spec)
        
    return page_spec

def run(queue, all_spec):
    while True:
        if queue.empty():
            print('Killing', mp.current_process().name)
            break
        brand, num_page = queue.get()
        print(brand, num_page)

        result = fetch_brand_page_spec(brand, num_page)
        all_spec += result


if __name__=='__main__':
    brands = ['OPPO', 'Samsung', 'Apple', 'Realme', 'Vivo', 'Xiaomi', 'Infinix', 'Nokia']
    num_pages = 100
    n_workers = 5

    queue = mp.Queue()
    manager = mp.Manager()
    all_spec = manager.list()

    for brand, num_page in itertools.product(brands, range(1, num_pages)):
        queue.put((brand, num_page))
    
    processes = [mp.Process(target=run, args=(queue, all_spec, )) for _ in range(n_workers)]

    for proc in processes:
        proc.start()
    
    for proc in processes:
        proc.join()

    all_spec = list(all_spec)
    all_spec = pd.DataFrame.from_records(all_spec)
    all_spec.to_csv('phone_data.csv')