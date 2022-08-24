# otodom-scraper

Simple tool to scrap polish real estate website (otodom.pl) and visiualise scraped data on AWS


## Installation

X11 display server protocol without any display
```bash
sudo apt install -y unzip xvfb libxi6 libgconf-2-4
```
Download and install latest stable version of google chrome
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```
Install selenium, webdriver-manager and boto3 for your python enviorment 
```bash
pip install selenium webdriver-manager boto3
```
    
## Scraping

To startscraping, run the following command

```bash
cd scrapyhouses/
scrapy crawl houses
```

