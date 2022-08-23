import time
import scrapy
import boto3
import re
# from inline_requests import inline_requests


class HousesSpider(scrapy.Spider):
    name = 'houses'
    allowed_domains = ['otodom.pl']
    page_counter = 1

    dynamodb_client = boto3.client('dynamodb')
    Houses_table = 'houses4'
    
    timestamp = int(float(time.time()))
    added_houses = 0

    def start_requests(self):
        urls = [ f'https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/cala-polska?limit=72&page={i}&by=LATEST&direction=DESC'
            for i in range(1, 32)
        ]
        for url in urls:
            time.sleep(1)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        def city_check(city):
            comma_position = city.find(',')
            return city[:comma_position]

        def room_check(room):
            space_position = room.find(' ')
            return room[:space_position]

        houses_listings = response.css('a[data-cy="listing-item-link"]')
        houses_listings = houses_listings[3:len(houses_listings)]
        for a in houses_listings:
            price = a.css('div')[1].css('span::text').getall()[0].replace(u'\xa0', u'').replace(u'zł', u'').replace(u',', u'.')
            try:
                price = int(float(price))
            except ValueError:
                price = 0
                
            if price == 0 or a.get().find('Odświeżony') != -1: continue
            
            link = a.xpath('@href').get()

            self.added_houses += 1

            title = a.css('div')[0].css('h3::text').get()
            city = city_check((a.css('p').css('span::text').get()))
            rooms = room_check((a.css('div')[1].css('span::text').getall()[1]))

            area = a.css('div')[1].css('span::text').getall()[2].replace(
                u' m²', u'')
            area = round(float(area), 2)

            price_meter = round(price / area, 2)
            hash_h = hash(title + str(price))

            item = {
                'title': {
                    'S': title
                },
                'city': {
                    'S': city
                },
                'price': {
                    'S': str(price)
                },
                'rooms': {
                    'S': rooms
                },
                'area': {
                    'S': str(area)
                },
                'meter_price': {
                    'S': str(price_meter)
                },
                'HouseID': {
                    'S': str(hash_h)
                },
                'timestamp': {
                    'S': str(self.timestamp)
                }
            }
            
            if self.added_houses % 3 :
                print(link)
                time.sleep(2)
                yield scrapy.Request(url='https://www.otodom.pl' + link, callback=self.parse_houses, meta={'hero_item': item})
            else:
                resp = self.dynamodb_client.put_item(TableName = self.Houses_table, Item = item)

    def parse_houses(self, response):
        item = response.meta.get('hero_item')
        body = response.css('body').get()
        
        day = re.search('Data dodania: ([0-9]*) dzień temu', body)
        days = re.search('Data dodania: ([0-9]*) dni temu', body)
        week = re.search('Data dodania: ([0-9]*) tydzień temu', body)
        weeks = re.search('Data dodania: ([0-9]*) tygodni temu', body)
        month = re.search('Data dodania: ([0-9]*) miesiąc temu', body)
        months = re.search('Data dodania: ([0-9]*) miesięcy temu', body)
        year = re.search('Data dodania: ([0-9]*) rok temu', body)
        years = re.search('Data dodania: ([0-9]*) lata temu', body)
        bools = {"day": day, 'days': days, 'week': week, 'weeks': weeks, 'month': month, 'months': months, 'year': year, 'years': years}
        if (day == None and days == None and week == None and weeks == None and month == None and months == None and year == None and years == None):
            resp = self.dynamodb_client.put_item(TableName = self.Houses_table, Item = item)
            yield {'item': item}
        else:
            raise scrapy.exceptions.CloseSpider(reason=f"Scraped {self.added_houses} houses data from last 24 hours / " + response.url + ' ' + str(bools))