from PyPDF2 import PdfFileReader
import re
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import itertools
import requests
import io


def searchSession(search: str = "1LIFE HEALTHCARE"):
    """ Search wikipedia and get most relevant url link to the search term
    """

    S = requests.Session()

    URL = "https://en.wikipedia.org/w/api.php"

    PARAMS = {
        "action": "opensearch",
        "format": "json",
        "namespace": 0,
        "search": search
    }

    R = S.get(url=URL, params=PARAMS)

    return R.json()


def getSP500Companies():

    soup = BeautifulSoup(requests.get(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies").text)
    sp500 = soup.find_all("table")[0]
    sp500_changes = soup.find_all("table")[1]

    l = []
    for item in sp500.find_all("td"):
        href = item.find('a', href=re.compile(r'/wiki/*'))
        if href:
            title = re.findall(">(.*?)<", str(href))
            link = re.findall('href="(.*?)"', str(href))
            if len(title) > 0 and len(link) > 0:
                l.append((title[0], link[0],))

    return l


def Russell3000Companies(url: str = 'https://content.ftserussell.com/sites/default/files/ru3000_membershiplist_20210628.pdf'):

    response = requests.get(url)

    pageitems, i = [], 0

    with io.BytesIO(response.content) as f:

        pdf = PdfFileReader(f)
        information = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()

        for page in range(number_of_pages - 1):  # since last page is pure content

            page = pdf.getPage(page)

            page_content = page.extractText()

            pageitems.append(str(page_content).split("\n"))

    upperTickers = [i for i in itertools.chain.from_iterable(
        pageitems) if i.isupper()]

    companies = pd.DataFrame([upperTickers[n: n + 2] for n in range(
        0, len(upperTickers), 2)], columns=['Company Names', 'Ticker'])

    return companies


def getUSExchangeStocks():
    nyse_denominations = ["0%E2%80%939", "A", "B", "C", "D", "E", "F", "G", "H", "I",
                          "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

    l = []

    for denomination in tqdm(nyse_denominations):

        soup = BeautifulSoup(requests.get(
            f"https://en.wikipedia.org/wiki/Companies_listed_on_the_New_York_Stock_Exchange_({denomination})").text)
        # First table is the one that allows u to browse
        items = soup.find_all("table")[1].find_all("td")

        for item in items:
            href = item.find('a', href=re.compile(r'/wiki/*'))
            if href:
                title = re.findall(">(.*?)<", str(href))
                link = re.findall('href="(.*?)"', str(href))
                if len(title) > 0 and len(link) > 0:
                    l.append((title[0], link[0],))

    u = []

    nasdaq_denominations = ["0", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
                            "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

    for denomination in tqdm(nasdaq_denominations):

        soup = BeautifulSoup(requests.get(
            f"https://en.wikipedia.org/w/index.php?title=Category:Companies_listed_on_the_Nasdaq&from={denomination}").text)

        atags = [i for i in list(map(lambda x: x.find(
            'a', href=re.compile(r'^/wiki/*')), soup.find_all("li"))) if i != None]

        for item in atags:
            title = re.findall(">(.*?)<", str(item))
            link = re.findall('href="(.*?)"', str(item))
            if len(title) > 0 and len(link) > 0 and ":" not in link[0] and title[0] != "":
                u.append((title[0], link[0],))

    listed_companies = pd.DataFrame(
        l + u, columns=['Company Name', 'Link']).drop_duplicates()

    return listed_companies
