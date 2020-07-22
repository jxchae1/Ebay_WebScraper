# How the program works:
# 1.Make a request to ebay.com and get a page using  get_page(url)
# 2.Collect data from each detail page using get_detail_data(soup)
# 3.Collect all links to detail pages of each product using get get_index_data(soup)
# 4.Put scraped data into a csv file using def write_csv(data, url)

import sys
import requests
from bs4 import BeautifulSoup
import csv


def get_page(url):
    # requests.get makes a request to a web page, and returns status code
    # response.ok returns True if status_code is less than 200, otherwise False
    response = requests.get(url)

    if not response.ok:
        print('Server responded: ', response.status_code)
    else:
        # BS constructor takes two arguments
        # first is the HTML code of the page
        # second is the parser used to parse the HTML code
        soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def get_detail_data(soup):
    # creates title, price, and shipping info

    try:
        title = soup.find('h1', id='itemTitle').contents[1]
    except NameError:
        print("Title: Unexpected error:", sys.exc_info()[0])
        title = ''

    try:
        if soup.find('span', id='prcIsum_bidPrice') is None:
            p = soup.find('span', id='prcIsum')
            if p is None:
                p = soup.find('span', id='mm-saleDscPrc')
        else:
            p = soup.find('span', id='prcIsum_bidPrice')
        p = p.text.strip()
        currency, price_with_sign = p.split(' ')
        tmp = price_with_sign[1:]
        tmp = tmp.split('/')
        tmp = tmp[0].replace(',', '')
        price = float(tmp)
    except (ValueError, TypeError, NameError):
        print("Price: Unexpected error:", sys.exc_info()[0])
        currency = ''
        price = ''

    try:
        shipping = soup.find('span', id='fshippingCost')
        if shipping is None:
            shipping = soup.find('span', id='shSummary').text.strip()
            if shipping.find('FREE') < 0:
                shippingCost = 0
            else:
                shippingCost = 0
        else:
            shipping = shipping.text.strip()
            if shipping == 'FREE':
                shippingCost = 0
            else:
                shippingCost = float(shipping[1:])

    except (ValueError, TypeError, NameError):
        print("Shipping: Unexpected error:", sys.exc_info()[0])
        shippingCost = 0

    # creates dictionary
    data = {
        'title': title,
        'price': price_with_sign,
        'shipping': shipping,
        'total cost': '$' + str(price + shippingCost)
    }
    return data


def get_index_data(soup):
    try:
        links = soup.find_all('a', class_='s-item__link')
    except (RuntimeError, TypeError, NameError):
        print("Links: Unexpected error:", sys.exc_info()[0])
        links = []

    urls = [item.get('href') for item in links]
    return urls


def write_csv(data, url):
    # if the 'open' function finds the following csv name, it will open it
    # otherwise, it will create a new file with the output.csv file name
    # the second argument 'a' is used to append each row
    # csvFile is the variable used to store the 'open' function
    with open('output.csv', 'a') as csvFile:
        row = [data['title'], data['price'], data['shipping'], data['total cost'], url]
        # csv.writer() function is used to create a writer object
        writer = csv.writer(csvFile)
        # writer.writerow() function is used to write single rows to the CSV file
        writer.writerow(row)


def main():
    url = 'https://www.ebay.com/sch/i.html?_nkw=olympic+weight+sets&_pgn=1'

    # stores list of all the urls
    products = get_index_data(get_page(url))

    # for each link in the list of urls, creates a data dictionary for each url
    for link in products:
        data = get_detail_data(get_page(link))
        write_csv(data, link)


if __name__ == '__main__':
    main()
