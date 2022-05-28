import datetime as dt

from time import sleep

import yfinance as yf
import matplotlib.pyplot as plt

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://www.binance.com/en/support/announcement/c-48?navId=48"
PATH = "./driver/chromedriver.exe"
TIMEOUT = 5

chrome_options = Options()
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument("--headless")

def get_listings():
    """
    Scrapes binance announcements for new coins
    """
    driver = webdriver.Chrome(PATH, options=chrome_options)
    driver.get(URL)

    sleep(TIMEOUT)

    listings = {}
    elems = driver.find_elements_by_xpath("//a[@href]")

    for elem in elems:
        
        if len(elem.get_attribute("href")) == 80:
            text = elem.find_element_by_tag_name("div").text
            
            if "Binance Will List" in text:
                text = text[18:-10]
                coin_dict = {}
                coin_dict["link"] = elem.get_attribute("href")
                coin_dict["date"] = elem.find_element_by_tag_name("h6").text

                listings[text] = coin_dict
    driver.quit()
    return listings

def get_price(ticker: str, listing_date: dt.datetime, withdrawal_date: dt.datetime):
    """
    ticker: ticker of the coin
    listing_date: date of the listing (anouncement) announcement on binance
    withdrawal_date: date when binance will allow withdrawals 
    """
    coin = yf.Ticker(f"{ticker}-USD")
    hist_df = coin.history(period="1y")
    hist_df = hist_df[(hist_df.index >= listing_date) & (hist_df.index <= withdrawal_date)]
    hist_df = hist_df.drop(['Dividends','Stock Splits', 'Volume', 'Low'], axis=1)
    return hist_df

def convert_date(date: str):
    date = date.split('-')
        
    if int(date[1]) > 10:
        date[1] = date[1][1:]
        
    if int(date[2]) > 10:
        date[2] = date[2][1:]

    date = [int(nr) for nr in date]
    return date

def convert_ticker(listing: str):
    ticker = listing
    start_idx = ticker.index('(')
    end_idx = ticker.index(')')
    ticker = ticker[start_idx+1:end_idx]

    return ticker

def plot_prices(dfs):
    
    number_of_subplots = len(dfs)
    for i,v in enumerate(range(number_of_subplots)):
        v = v+1
        ax1 = plt.subplot(number_of_subplots,1,v)
        ax1.plot(dfs[i])

    plt.show()

if __name__ == "__main__":
    listings = get_listings()
    
    prices = []

    for listing in listings:
        date = listings[listing]["date"]
        date = convert_date(date)
        listing_date = dt.datetime(date[0], date[1], date[2])
        withdrawal_date = dt.datetime(date[0], date[1], date[2]+1)

        if 'and' in listing:
            listing = listing.split('and')
            tickers = [convert_ticker(l) for l in listing]
            
            for ticker in tickers:
                df = get_price(ticker, listing_date, withdrawal_date)
                prices.append(df)

        else:
            ticker = convert_ticker(listing)
            df = get_price(ticker, listing_date, withdrawal_date)
            prices.append(df)
    
    #plot_prices(prices)
    print(prices)
        
    #TODO go through all pages of listings not only first one
    #TODO setup to continously run via cloud
    #TODO combine with email notification
