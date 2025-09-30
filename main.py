import requests
import bs4
import time
import local as lcl


def check(element, start_idx):
    """
    Checks for the presence of an element and returns its text from the specified index.

    If the element is missing, returns the value from lcl.MISSING_INFORMATION.

    Args:
    element (bs4.element.Tag | None): HTML element to check.
    start_idx (int): Index to start with.

    Returns:
    str: Element text or a message indicating missing information.
    """
    return element.text[start_idx:] if element else f"{lcl.MISSING_INFORMATION}"


def get_last_page(search_query):
    """
    Gets the number of the last page of search results.

    Args:
    search_query (str): Search query string.

    Returns:
    int: Number of the last page of search results.
    """
    url = f'https://obuv-tut2000.ru/magazin/search?gr_smart_search=1&search_text={search_query}'
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    last_page_tag = soup.find("li", class_="page-num page_last")
    return int(last_page_tag.text) if last_page_tag else 1


def generate_product_urls(search_query):
    """
    Generates URLs of all products for a search query, taking into account pagination.

    Args:
    search_query (str): Search query string.

    Yields:
    str: Full URL of each found product.
    """
    total_pages = get_last_page(search_query)
    for page in range(0, total_pages + 1):
        if page==0:
            url = f'https://obuv-tut2000.ru/magazin/search?&gr_smart_search=1&search_text={search_query}'
        else:
            url = f'https://obuv-tut2000.ru/magazin/search?p={page}&gr_smart_search=1&search_text={search_query}'
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        items = soup.find_all("div", class_="product-item__top")
        for item in items:
            href = item.find("a").get("href")
            yield "https://obuv-tut2000.ru" + href


def parse_product(url):
    """
    Parses product data from its page.

    Args:
    url (str): URL of the product page.

    Returns:
    dict | None: A dictionary containing product information, or None if no data is available.
    """
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    data = soup.find("div", class_="card-page")
    if not data:
        return None

    try:
        name = data.find("h1").text
        country = check(data.find("div", class_="gr-vendor-block"), 0).strip()
        article = data.find("div", class_="shop2-product-article").text
        color = data.find("div", class_="option-item cvet odd").text[4:]
        tipe = data.find("h1").text.split()
        tipe_1 = tipe[0]
        upper_material = data.find("div", class_="option-item material_verha_960 odd").text[14:]
        size = data.find("div", class_="option-item razmery_v_korobke even").text[7:]
        season = check(data.find("div", class_="option-item sezon even"), 5)
        price_str = data.find("strong").text.strip()

        
        price_value = int(price_str) if price_str else 0

        return {
            'name': name,
            'country': country,
            'article': article,
            'color': color,
            'type': tipe_1,
            'upper_material': upper_material,
            'size': size,
            'season': season,
            'price': price_value
        }
    except AttributeError:
        return None


def save_results(products, filename="sorted_products.txt"):
    """
    Saves a list of products to a text file.

    Args:
    products (list): List of dictionaries with product information.
    filename (str, optional): File name to save. Defaults to "sorted_products.txt".
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for product in products:
            f.write(f"{lcl.NAME}: {product['name']}\n")
            f.write(f"{lcl.COUNTRY}: {product['country']}\n")
            f.write(f"{lcl.ARTICLE}: {product['article']}\n")
            f.write(f"{lcl.COLOR}: {product['color']}\n")
            f.write(f"{lcl.TYPE_OF_SHOE}: {product['type']}\n")
            f.write(f"{lcl.UPPER_MATERIAL}: {product['upper_material']}\n")
            f.write(f"{lcl.SIZE}: {product['size']}\n")
            f.write(f"{lcl.SEASON}: {product['season']}\n")
            f.write(f"{lcl.PRICE}: {product['price']} руб.\n")
            f.write("-"*40 + "\n")


search_query = input(f"{lcl.ENTER_SEARCH_QUERY}:")
products = []
for url in generate_product_urls(search_query):
    time.sleep(3)
    product_data = parse_product(url)
    if product_data:
        products.append(product_data)


products.sort(key=lambda x: x['price'])


save_results(products)


print(f"{lcl.PRODUCT_INFORMATION_IN_THE_FOLLOWING_FILE}:", "sorted_products.txt" )
