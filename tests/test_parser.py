from src.parser import parse_listing, parse_product


def test_listing_links_and_next_page():
    html = '<article class="product_pod"><h3><a href="a.html">A</a></h3></article><li class="next"><a href="page-2.html">next</a></li>'
    products, next_page = parse_listing(html, "https://books.toscrape.com/catalogue/page-1.html")
    assert products == ["https://books.toscrape.com/catalogue/a.html"]
    assert next_page == "https://books.toscrape.com/catalogue/page-2.html"


def test_product_fields():
    html = '''<ul class="breadcrumb"><li><a href="/">Home</a></li><li><a href="/catalogue.html">Books</a></li><li><a href="/cat.html">Travel</a></li></ul>
    <div class="product_main"><h1>Sample</h1><p class="price_color">£12.99</p><p class="star-rating Three"></p><p class="availability">In stock (4 available)</p></div>
    <table class="table table-striped"><tr><th>UPC</th><td>ABC</td></tr><tr><th>Number of reviews</th><td>2</td></tr></table>'''
    product = parse_product(html, "https://books.toscrape.com/catalogue/sample.html")
    assert product["title"] == "Sample"
    assert product["category"] == "Travel"
    assert product["rating"] == 3
    assert product["stock_quantity"] == 4
    assert product["upc"] == "ABC"
