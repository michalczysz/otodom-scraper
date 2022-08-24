# otodom-scraper
Simple tool to scrap real estate site and visiualise this data on AWS

#Installation
1. X11 display server protocol without any display
	```sh
	sudo apt install -y unzip xvfb libxi6 libgconf-2-4
	```
2. Download and install latest stable version of google chrome
	```sh
		wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
		sudo apt install ./google-chrome-stable_current_amd64.deb
	```
3. Install selenium, webdriver-manager and boto3 for your python enviorment
	```sh
		pip install selenium webdriver-manager boto3
	```
*Rember to configure your AWS-cli. Otherwise boto3 library will not connect to your danamodb database
#Scraping
Now you can start by typing
```sh
	cd scrapyhouses
	scrapy crawl houses
```
