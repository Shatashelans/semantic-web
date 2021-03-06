import requests
import bs4 as bs
import re
from xml.etree.ElementTree import Element, SubElement, ElementTree
from xml.dom.minidom import parseString


# Parsing necessary page
def parser(link):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}
    res = requests.get(link, headers=headers)
    open('data/amazon.html', 'wb').write(bytes(res.text, encoding='UTF-8'))


# Page scrapping
def page_scrapping(text_of_page):
    soup = bs.BeautifulSoup(text_of_page, features='lxml')
    items_list = str(soup.find('ul'))
    soup = bs.BeautifulSoup(items_list, features='lxml')
    items_list = soup.find_all('li', class_='s-result-item celwidget')
    return items_list


def filter_text(text_of_items):
    items_matrix = []
    heads_of_items = list(map(lambda x: re.findall(r'(.+) [(]', x)[0], text_of_items))
    items_matrix.append(heads_of_items)
    companies_of_items = list(map(lambda x: re.findall(r'[)]by (\w+)[$]', x)[0], text_of_items))
    items_matrix.append(companies_of_items)
    price_of_items = list(map(lambda x: re.findall(r'\d+[.]\d+', re.findall(r'[$]\d+[.]\d+', x)[0])[0], text_of_items))
    items_matrix.append(price_of_items)
    rating_of_item = list(map(lambda x: re.findall(r'\d[.]\d', re.findall(r'\n\d[.]\d', x)[0])[0], text_of_items))
    items_matrix.append(rating_of_item)
    amount_of_customers = list(
        map(lambda x: re.findall(r'\d+[,]\d+|\d+', re.findall(r'\n\d+[,]\d+|\n\d+', x)[1])[0], text_of_items))
    items_matrix.append(amount_of_customers)
    return items_matrix


def xml_forming(items_matrix):
    items_list = Element('items_list')
    for i in range(len(items_matrix[0])):
        phone = SubElement(items_list, 'phone')
        phone.set('id', 'result_' + str(i))
        model_name = SubElement(phone, 'model_name')
        model_name.text = items_matrix[0][i]
        company_name = SubElement(phone, 'company_name')
        company_name.text = items_matrix[1][i]
        price = SubElement(phone, 'price')
        price.set('currency', 'dollar')
        price.text = items_matrix[2][i]
        rating = SubElement(phone, 'rating')
        rating.set('max_value', '5')
        rating.text = items_matrix[3][i]
        amount_of_customers = SubElement(phone, 'amount_of_customers')
        amount_of_customers.text = items_matrix[4][i]
    tree = ElementTree(items_list)
    tree.write('data/amazon.xml', encoding='UTF-8', xml_declaration=True)
    return tree


def prettify_xml():
    with open('data/amazon.xml', 'r') as file:
        xml_text = file.read()
        prettified_xml = parseString(xml_text).toprettyxml()
        file.close()
    with open('data/amazon.xml', 'w') as file:
        file.write(prettified_xml)
        file.close()


if __name__ == '__main__':
    parser('https://www.amazon.com/b?node=18637575011&pf_rd_p=40ed81c0-6271-4813-bb5a-c65127ad0c47&pf_rd_r=D1SM2DP8QFFYXXRGS5S5')
    with open('data/amazon.html', 'r') as file:
        data = file.read()
    scrapped_data = page_scrapping(data)
    text_of_items = list(map(lambda item: item.text, scrapped_data))
    items_matrix = filter_text(text_of_items)
    xml = xml_forming(items_matrix)
    prettify_xml()