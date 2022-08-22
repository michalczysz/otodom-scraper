import time
import scrapy
import boto3

class HousesSpider(scrapy.Spider):
    name = 'houses'
    allowed_domains = ['otodom.pl']
    page_counter = 1
    start_urls = ['https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/cala-polska?limit=72&page='+ str(page_counter) +'&by=LATEST&direction=DESC' ]
    
    dynamodb_client = boto3.client('dynamodb')
    Houses_table = 'houses2'
    
    last_HouseID = 0
    hash_cache = []
    
    def parse(self, response):
        def city_check(city):
            comma_position = city.find(',')
            return city[:comma_position]
        
        def room_check(room):
            space_position = room.find(' ')
            return room[:space_position]
            
        # if self.page_counter == 1 or self.page_counter % == 5:
            
        
        raw_body = response.css('body').getall()
        position = raw_body[0].find('totalPages":')
        page_count = int(raw_body[0][position + 12 : position + 16])
        
        litings = response.css('a[data-cy="listing-item-link"]') #response.css('article')
        for list_a in litings:
            list = list_a.css('article')
            price = list.css('div')[1].css('span::text').getall()[0].replace(u'\xa0', u'').replace(u'zł', u'').replace(u',', u'.')
            
            try: 
                price = int(float(price))
            except ValueError:
                price = 0
                
            if price == 0 : continue # or list.get().find('Odświeżony')
            self.last_HouseID += 1
            HouseID = self.last_HouseID
            title = list.css('div')[0].css('h3::text').get()
            
            city = city_check((list.css('p').css('span::text').get()))
            rooms = room_check((list.css('div')[1].css('span::text').getall()[1]))
            
            area = list.css('div')[1].css('span::text').getall()[2].replace(u' m²', u'')
            area = round(float(area), 2)
            price_meter = round(price/area, 2)
            hash_h = hash(title+str(price))
            self.hash_cache.append(hash_h)
            item = {'title':  {'S':title}, 
                    'city': {'S':city}, 
                    'price': {'S':str(price)}, 
                    'rooms': {'S':rooms}, 
                    'area': {'S':str(area)}, 
                    'meter_price': {'S':str(price_meter)}, 
                    'hash': {'S':str(hash_h)},
                    'HouseID': {'S': str(HouseID)},
                    'timestamp': {'S': str(int(float(time.time())))}
                    }
            #yield {'title': title, 'city': city, 'price': price, 'rooms': rooms, 'area': area, 'meter_price': price_meter, 'hash': hash_h}
            resp = self.dynamodb_client.put_item(TableName = self.Houses_table, Item = item)
        self.page_counter += 1
        yield {'page': self.page_counter, 'counter': HouseID}
        if self.page_counter <= page_count: #self.page_counter < 2 and 
            time.sleep(3)
            next_url = 'https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/cala-polska?limit=72&page='+ str(self.page_counter) +'&by=LATEST&direction=DESC'
            yield scrapy.Request(next_url, callback=self.parse)