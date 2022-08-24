
# otodom-scraper

Simple tool to scrap polish real estate website (otodom.pl) and visiualise scraped data on AWS Quicksight.

Project consists of few AWS applications. 
Every day Lambda function starts EC2 instance, which when loaded start scraping. Scraping script from this repo, will be sending quieries with scraped houses to dynamodb.
AWS doesnt allow directly read from dynamodb to Quicksight, so data database hub AWS Athena. AWS Athena cannot reads directly from dynamodb, so it needs to invoke special lambda function that will return dynamodb data.
Returned data to Athena are stored in S3 bucket, which allow us us to reach tem by making normal queries, therefore enabling us to use those data in Quicksight as well.  
 
Diagram of architecture:
![App Screenshot](https://publicmichalczysz.s3.eu-central-1.amazonaws.com/otodom-scraper-diagram.png)
## Installation
To add lambda function that will [start EC2 instance at specific time.](https://aws.amazon.com/premiumsupport/knowledge-center/start-stop-lambda-eventbridge/)

To add script that will run on linux (ubuntu server in this case) startup, check [this article.](https://linuxconfig.org/how-to-run-script-on-startup-on-ubuntu-22-04-jammy-jellyfish-server-desktop)

X11 display server protocol without any display
```bash
sudo apt install -y unzip xvfb libxi6 libgconf-2-4
```
Download and install latest stable version of google chrome
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```
Install scrapy, selenium, webdriver-manager and boto3 for your python enviorment 
```bash
pip install scrapy selenium webdriver-manager boto3
```

Do not forget to configure your AWS-cli.
## Scraping

To startscraping, run the following commands

```bash
cd scrapyhouses/
scrapy crawl houses
```


## Results

![App Screenshot](https://publicmichalczysz.s3.eu-central-1.amazonaws.com/QuickSightOutput.png)

