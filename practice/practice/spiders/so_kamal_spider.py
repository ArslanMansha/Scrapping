# collections[any]=[collection_link, collection_url, collection_id, collection_discount_percentage]
import scrapy
import json
import re
from practice.items import SoKamalItem


class SoKamalSpider(scrapy.Spider):
    name = 'kamal'

    def start_requests(self):
        urls = ["https://fishry.azure-mobile.net/tables/link_list?%24filter=(storeID%20eq%20'480EFD74-078"
                "D-4CF2-AC68-270940ED408F')&%24top=1000"]
        yield scrapy.Request(url=urls[0], callback=self.parse,
                             headers={"X-ZUMO-APPLICATION": "egepBriQNqIKWucZFzqpQOMwdDmzfs16"})

    def get_collections(self, raw_collections):
        collections = []
        for section in range(len(raw_collections) - 2):
            for category in range(len(raw_collections[section]['list'])):
                if len(raw_collections[section]['list'][category]['list']) == 0:
                    if raw_collections[section]['list'][category]['linkType'] == 'http':
                        collections = collections + [[re.findall('\/e[\w\W]+\?',
                                                                 str(raw_collections[section]['list'][category]['linkHttp']))[0][1:-1],
                                                     raw_collections[section]['list'][category]['linkHttp']]]
                    else:
                        collections = collections + [[raw_collections[section]['list'][category]['linkCollection'],
                                                     'https://sokamal.com/collections/{}'.format(
                                                        raw_collections[section]['list'][category]['linkCollection'])]]
                else:
                    for sub_category in range(len(raw_collections[section]['list'][category]['list'])):
                        if raw_collections[section]['list'][category]['list'][sub_category]['linkType'] == 'http':
                            collections = collections + [[re.findall('\/e[\w\W]+\?',
                                                         str(raw_collections[section]['list'][category]['list'][sub_category]['linkHttp']))[0][1:-1],
                                                     raw_collections[section]['list'][category]['list'][sub_category]['linkHttp']]]
                        else:
                            collections = collections + [[raw_collections[section]['list'][category]['list'][sub_category]['linkCollection'],
                                                         'https://sokamal.com/collections/{}'.format(
                                                        raw_collections[section]['list'][category]['list'][sub_category]['linkCollection'])]]
        return collections

    def parse(self, response):
        json_response = json.loads(response.body_as_unicode())
        raw_collections = json_response[1]['link_list']
        raw_collections = raw_collections.replace('\\', '')
        raw_collections = json.loads(raw_collections)
        collections = self.get_collections(raw_collections)
        yield response.follow("https://fishry.azure-mobile.net/tables/collection?%24filter=((collectionVisibility%20eq%"
                              "20true)%20and%20(storeID%20eq%20'480EFD74-078D-4CF2-AC68-270940ED408F'))&%24top=1000",
                              headers={"X-ZUMO-APPLICATION": "egepBriQNqIKWucZFzqpQOMwdDmzfs16"},
                              meta={'collections': collections}, callback=self.parse_collection_id)

    def parse_collection_id(self, response):
        json_response = json.loads(response.body_as_unicode())
        collections = response.meta['collections']
        for counter in range(len(collections)):
            for response_collection in range(len(json_response)):
                if collections[counter][0] == json_response[response_collection]['collectionUrl']:
                    collections[counter] = collections[counter] + [json_response[response_collection]['id']]
                    if json_response[response_collection]['campaign_label'] is None:
                        collections[counter] = collections[counter] + [0]
                    else:
                        collections[counter] = collections[counter] + [int(re.findall(r'[\d]+',
                                                                          str(json_response[response_collection]['campaign_label']))[0])]

        for collection in collections:
            form_data = {'collection_id[]': collection[2], 'collection_inclusion': 'true', 'order_by': '__createdAt',
                         'skip': '0', 'status': 'true', 'storeID': '480EFD74-078D-4CF2-AC68-270940ED408F',
                         'take': '2000', }
            header = {'Content-Type': 'application/x-www-form-urlencoded'}
            yield scrapy.FormRequest("https://fishry-api-live.azurewebsites.net/collection_request", method='POST',
                                     headers=header, formdata=form_data, callback=self.parse_product,
                                     meta={'discount': collection[3]})

    def parse_product(self, response):
        json_response = json.loads(response.body_as_unicode())
        for iterator in range(len(json_response)):
            images = json_response[iterator]['productImage']
            images = images.replace('\\', '')
            images = json.loads(images)
            image_urls = []
            for count in range(len(images)):
                image_urls = image_urls + ["https://fishry-image.azureedge.net/product/" + images[str(count)]['Image']]

            collections = json_response[iterator]['productCollections']
            collections = collections.replace('\\', '')
            collections = json.loads(collections)
            collection_keys = list(collections.keys())
            collection_names = []
            for collection_key in collection_keys:
                collection_names = collections[collection_key]['name']
            item = SoKamalItem()
            item['name'] = json_response[iterator]['productName']
            item['ID'] = json_response[iterator]['id']
            item['image'] = image_urls
            item['description'] = json_response[iterator]['productDescription']
            item['weblink'] = "https://sokamal.com/product/" + json_response[iterator]['productUrl']
            item['collection'] = collection_names
            item['price'] = json_response[iterator]['productPrice']
            item['storeID'] = json_response[iterator]['storeID']
            item['product_type'] = json_response[iterator]['productType']
            item['product_vendor'] = json_response[iterator]['productVendor']
            item['productSKU'] = json_response[iterator]['productSKU']
            item['product_barcode'] = json_response[iterator]['productBarcode']
            item['product_varients'] = json.loads(json_response[iterator]['productVarients'])
            item['discount_price'] = response.meta['discount'] / 100 * json_response[iterator]['productPrice']
            yield item
