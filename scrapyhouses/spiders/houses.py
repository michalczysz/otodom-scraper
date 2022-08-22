import time
import scrapy
import boto3
# from inline_requests import inline_requests


class HousesSpider(scrapy.Spider):
    name = 'houses'
    allowed_domains = ['otodom.pl']
    page_counter = 1
    start_urls = [
        'https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/cala-polska?limit=72&page='
        + str(page_counter) + '&by=LATEST&direction=DESC'
    ]

    dynamodb_client = boto3.client('dynamodb')
    Houses_table = 'houses3'

    last_HouseID = 0
    hash_cache = []
    
    item={}

    def start_requests(self):
        urls = [
            f'https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/cala-polska?limit=24&page={i}&by=LATEST&direction=DESC'
            for i in range(1, 2)
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        def city_check(city):
            comma_position = city.find(',')
            return city[:comma_position]

        def room_check(room):
            space_position = room.find(' ')
            return room[:space_position]

        for a in response.css('a[data-cy="listing-item-link"]'):
            # output = {}
            price = a.css('div')[1].css('span::text').getall()[0].replace(
                u'\xa0', u'').replace(u'zł', u'').replace(u',', u'.')
            try:
                price = int(float(price))
            except ValueError:
                price = 0
            if price == 0 : continue
            
            link = a.xpath('@href').get()

            self.last_HouseID += 1
            HouseID = self.last_HouseID

            title = a.css('div')[0].css('h3::text').get()
            city = city_check((a.css('p').css('span::text').get()))
            rooms = room_check((a.css('div')[1].css('span::text').getall()[1]))

            area = a.css('div')[1].css('span::text').getall()[2].replace(
                u' m²', u'')
            area = round(float(area), 2)

            price_meter = round(price / area, 2)
            hash_h = hash(title + str(price))
            self.hash_cache.append(hash_h)
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
                'hash': {
                    'S': str(hash_h)
                },
                'HouseID': {
                    'S': str(HouseID)
                },
                'timestamp': {
                    'S': str(int(float(time.time())))
                }
            }
            #yield {'title': title, 'city': city, 'price': price, 'rooms': rooms, 'area': area, 'meter_price': price_meter, 'hash': hash_h}

            print(link)
            yield scrapy.Request(url='https://www.otodom.pl' + link,
                                 callback=self.parse_houses, meta={'hero_item': item})

    def parse_houses(self, response):
        item = response.meta.get('hero_item')
        yield {"text": response.css('body').get().find('dni temu')}
        yield {"test": item}

    # @inline_requests
    # def parse(self, response):
    #     def city_check(city):
    #         comma_position = city.find(',')
    #         return city[:comma_position]

    #     def room_check(room):
    #         space_position = room.find(' ')
    #         return room[:space_position]

    #     raw_body = response.css('body').getall()
    #     position = raw_body[0].find('totalPages":')

    #     try:
    #         page_count = int(raw_body[0][position + 12 : position + 16])
    #     except ValueError:
    #         page_count = self.page_counter

    #     litings = response.css('a[data-cy="listing-item-link"]')
    #     litings = litings[3:len(litings)]
    #     for list_a in litings:

    #         #test = scrapy.Request('https://www.otodom.pl' + list_a.xpath('@href').get(), callback=inner_page)
    #         try:
    #             next_resp = yield scrapy.Request('https://www.otodom.pl' + list_a.xpath('@href').get())
    #             #urls.append(next_resp.url)
    #             print('xdddd->' + next_resp.response.css('div').get())
    #         except Exception:
    #             self.logger.info("Failed request ")

    #         list = list_a.css('article')
    #         price = list.css('div')[1].css('span::text').getall()[0].replace(u'\xa0', u'').replace(u'zł', u'').replace(u',', u'.')

    #         try:
    #             price = int(float(price))
    #         except ValueError:
    #             price = 0

    #         #if price == 0 : continue #or list.get().find('Odświeżony') != -1

    #         self.last_HouseID += 1
    #         HouseID = self.last_HouseID
    #         title = list.css('div')[0].css('h3::text').get()

    #         city = city_check((list.css('p').css('span::text').get()))
    #         rooms = room_check((list.css('div')[1].css('span::text').getall()[1]))

    #         area = list.css('div')[1].css('span::text').getall()[2].replace(u' m²', u'')
    #         area = round(float(area), 2)
    #         price_meter = round(price/area, 2)
    #         hash_h = hash(title+str(price))
    #         self.hash_cache.append(hash_h)
    #         item = {'title':  {'S':title},
    #                 'city': {'S':city},
    #                 'price': {'S':str(price)},
    #                 'rooms': {'S':rooms},
    #                 'area': {'S':str(area)},
    #                 'meter_price': {'S':str(price_meter)},
    #                 'hash': {'S':str(hash_h)},
    #                 'HouseID': {'S': str(HouseID)},
    #                 'timestamp': {'S': str(int(float(time.time())))}
    #                 }
    #         #yield {'title': title, 'city': city, 'price': price, 'rooms': rooms, 'area': area, 'meter_price': price_meter, 'hash': hash_h}
    #         resp = self.dynamodb_client.put_item(TableName = self.Houses_table, Item = item)
    #     self.page_counter += 1
    #     yield {'page': self.page_counter, 'counter': HouseID}
    #     if self.page_counter < 2 and self.page_counter <= page_count: #
    #         time.sleep(3)
    #         next_url = 'https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/cala-polska?limit=72&page='+ str(self.page_counter) +'&by=LATEST&direction=DESC'
    #         yield scrapy.Request(next_url, callback=self.parse)