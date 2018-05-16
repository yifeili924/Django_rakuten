# -*- coding: utf-8 -*-
import requests
import os
import dicttoxml
import requests
import xml.etree.ElementTree as ET

import scrapy
from webscraper_demo.items import WebscraperDemoItem
import re
import json
from scrapy.http import FormRequest
from scrapy.selector import Selector
import base64
import time
# from . import data
from testmodels import const
from testmodels.models import TestModels
import hashlib
from scrapy.utils.python import to_bytes


class ToScrapeSpiderXPath(scrapy.Spider):
    name = 'test4'
    base_url = "http://www.neimanmarcus.com"
    first_url = "http://www.neimanmarcus.com/en-jp/index.jsp"
    all_count = 0
    find_count = 0
    fail_count = 0
    page_size = 120
    parse_cat = False

    folder_insert_result = 'error'
    product_image_count = 0
    product_folder_count = 1
    image_result = 'error'
    def start_requests(self):
        if self.parse_cat:
            # '{"RWD.deferredContent.DeferredContentReqObj":{"contentPath":"/page_rwd/header/silos/silos.jsp","category":"cat000000","cacheKey":"r_responsiveDrawersHeader_JP_en"}}'
            data = "$b64$eyJSV0QuZGVmZXJyZWRDb250ZW50LkRlZmVycmVkQ29udGVudFJlcU9iaiI6eyJjb250ZW50UGF0aCI6Ii9wYWdlX3J3ZC9oZWFkZXIvc2lsb3Mvc2lsb3MuanNwIiwiY2F0ZWdvcnkiOiJjYXQwMDAwMDAiLCJjYWNoZUtleSI6InJfcmVzcG9uc2l2ZURyYXdlcnNIZWFkZXJfSlBfZW4ifX0$"
            post_url = self.base_url + "/en-jp/deferred.service"
            timestamp = str(time.time() * 1000)
            formdata = {'data': data,
                        'sid': 'getResponse',
                        'bid': 'DeferredContentReqObj',
                        'timestamp': timestamp}
            yield FormRequest(url=post_url, formdata=formdata, callback=self.parse_menubar)

        pageSize = '?pageSize=' + str(self.page_size)
        # for id in range(1,162):
        #     cat_info = TestModels.get_cat_info(id)
        #     if cat_info != None:
        #         href = cat_info[0].split(';')[0]
        #         cat = cat_info[1]
        #         url = href + pageSize
        #         TestModels.del_prod_info(cat)
        #         yield scrapy.Request(url=url, callback=self.parse_categorylink,
        #                              meta={'type': 0, 'url1': href, 'items_count': 0, 'find_count': 0, 'page_num': 0,
        #                                    'cat': cat})

        # initializing the found product counts
        TestModels.set_init_count()

        # creating one folder for initializing
        self.folder_insert_result = self.cabinet_foler_insert('nei_man1')

        cat_info = TestModels.get_cat_info(143)
        if cat_info != None:
            href = cat_info[0].split(';')[0]
            cat = cat_info[1]
            url = href + pageSize
            TestModels.del_prod_info(cat)
            # initializing the found product counts
            TestModels.set_init_count()
            yield scrapy.Request(url=url, callback=self.parse_categorylink,
                                 meta={'type': 0, 'url1': href, 'items_count': 0, 'find_count': 0, 'page_num': 0,
                                       'cat': cat})
    def parse_menubar(self, response):

        def extract_var(text, reg):
            return re.search(reg, text).groups()[0]

        TestModels.set_find_type(const.FIND_PROGRESS)

        href_all_list = []
        category_list = []
        json_data = json.loads(response.body)
        resp = Selector(text=json_data.get('RWD.deferredContent.DeferredContentRespObj', '').get('content', ''))

        # Women's Apparel , Shoes, Handbags
        silo_id = [2, 4, 5]
        cat0 = "Women's"
        cat1_array = ['Apparel', 'Shoes', 'Handbags']
        for id, cat1 in zip(silo_id, cat1_array):
            silo_li = '//li[@id="silo' + str(id) + '"]//div[@class="silo-column"]'
            categories = resp.xpath(silo_li)[1]
            href_list = categories.xpath('.//ul//a/@href').extract()
            first = True
            for href in href_list:
                if first:
                    first = False
                    continue
                href_all_list.append(href)
                cat2 = extract_var(href, r"en-jp/(.*?)/cat")
                category = cat0 + "\\" + cat1 + "\\" + str(cat2).replace("/", "\\")
                category_list.append(category)

        # Jewelry & Accessories
        silo_li = '//li[@id="silo6"]//div[@class="silo-column"]'
        categories = resp.xpath(silo_li)[1]
        href_list = categories.xpath('.//ul//a/@href').extract()
        first = True
        for href in href_list:
            if first:
                first = False
                continue
            href_all_list.append(href)
            cat2 = extract_var(href, r"en-jp/(.*?)/cat")
            category = cat0 + "\\" + str(cat2).replace("/", "\\")
            category_list.append(category)

        categories = resp.xpath(silo_li)[2]
        href_list = categories.xpath('.//ul//a/@href').extract()
        first = True
        for href in href_list:
            if first:
                first = False
                continue
            href_all_list.append(href)
            cat2 = extract_var(href, r"en-jp/(.*?)/cat")
            category = cat0 + "\\" + str(cat2).replace("/", "\\")
            category_list.append(category)

        href_list = categories.xpath('.//h6//a/@href').extract()
        first = True
        cat1 = "Accessories"
        for href in href_list:
            if first:
                first = False
                continue
            href_all_list.append(href)
            cat2 = extract_var(href, r"Accessories/(.*?)/cat")
            category = cat0 + "\\" + cat1 + "\\" + str(cat2).replace("/", "\\")
            category_list.append(category)

        # Beauty
        silo_li = '//li[@id="silo7"]//div[@class="silo-column"]'
        categories = resp.xpath(silo_li)[1]
        all_beauty = str(categories.xpath('.//h6//a/text()').extract()[0])
        cat1 = "Beauty"
        if all_beauty == ' All Beauty ':
            ul_list = categories.xpath('.//ul')[0]
            href_list = ul_list.xpath('.//a/@href').extract()
            for href in href_list:
                href_all_list.append(href)
                cat2 = extract_var(href, r"en-jp/(.*?)/cat")
                category = cat0 + "\\" + cat1 + "\\" + str(cat2).replace("/", "\\")
                category_list.append(category)

            ul_list = categories.xpath('.//ul')[1]
            href_list = ul_list.xpath('.//a/@href').extract()
            for href in href_list:
                href_all_list.append(href)
                cat2 = extract_var(href, r"en-jp/(.*?)/cat")
                category = cat0 + "\\" + cat1 + "\\" + str(cat2).replace("/", "\\")
                category_list.append(category)
            cat0 = "Men's"
            cat1 = "Cologne-Grooming"
            ul_list = categories.xpath('.//ul')[2]
            href_list = ul_list.xpath('.//a/@href').extract()
            for href in href_list:
                href_all_list.append(href)
                cat2 = extract_var(href, r"Cologne-Grooming/(.*?)/cat")
                category = cat0 + "\\" + cat1 + "\\" + str(cat2).replace("/", "\\")
                category_list.append(category)

            cat0 = "Women's"
            href_list = categories.xpath('.//h6//a/@href').extract()
            href_all_list.append(href_list[2])
            cat2 = extract_var(href_list[2], r"en-jp/(.*?)/cat")
            category = cat0 + "\\" + str(cat2).replace("/", "\\")
            category_list.append(category)
            href_all_list.append(href_list[4])
            cat2 = extract_var(href_list[4], r"en-jp/(.*?)/cat")
            category = cat0 + "\\" + str(cat2).replace("/", "\\")
            category_list.append(category)
            href_all_list.append(href_list[5])
            cat2 = extract_var(href_list[5], r"en-jp/(.*?)/cat")
            category = cat0 + "\\" + str(cat2).replace("/", "\\")
            category_list.append(category)
        else:
            categories = resp.xpath(silo_li)[0]
            ul_list = categories.xpath('.//ul')[1]
            href_list = ul_list.xpath('.//a/@href').extract()
            for href in href_list:
                href_all_list.append(href)
                cat2 = extract_var(href, r"en-jp/(.*?)/cat")
                category = cat0 + "\\" + cat1 + "\\" + str(cat2).replace("/", "\\")
                category_list.append(category)

            ul_list = categories.xpath('.//ul')[2]
            href_list = ul_list.xpath('.//a/@href').extract()
            for href in href_list:
                href_all_list.append(href)
                cat2 = extract_var(href, r"en-jp/(.*?)/cat")
                category = cat0 + "\\" + cat1 + "\\" + str(cat2).replace("/", "\\")
                category_list.append(category)

            ul_list = categories.xpath('.//ul')[3]
            href_list = ul_list.xpath('.//a/@href').extract()
            cat0 = "Men's"
            cat1 = "Cologne-Grooming"
            for href in href_list:
                href_all_list.append(href)
                cat2 = extract_var(href, r"Cologne-Grooming/(.*?)/cat")
                category = cat0 + "\\" + cat1 + "\\" + str(cat2).replace("/", "\\")
                category_list.append(category)

            cat0 = "Women's"
            href_list = categories.xpath('.//h6//a/@href').extract()
            href_all_list.append(href_list[4])
            cat2 = extract_var(href_list[4], r"en-jp/(.*?)/cat")
            category = cat0 + "\\" + str(cat2).replace("/", "\\")
            category_list.append(category)
            href_all_list.append(href_list[6])
            cat2 = extract_var(href_list[6], r"en-jp/(.*?)/cat")
            category = cat0 + "\\" + str(cat2).replace("/", "\\")
            category_list.append(category)
            href_all_list.append(href_list[7])
            cat2 = extract_var(href_list[7], r"en-jp/(.*?)/cat")
            category = cat0 + "\\" + str(cat2).replace("/", "\\")
            category_list.append(category)

        # The Man's Store
        cat0 = "Men's"
        silo_li = '//li[@id="silo8"]//div[@class="silo-column"]'
        categories = resp.xpath(silo_li)[1]
        href_list = categories.xpath('.//ul//a/@href').extract()
        for href in href_list:
            href_all_list.append(href)
            cat2 = extract_var(href, r"en-jp/(.*?)/cat")
            category = cat0 + "\\" + str(cat2).replace("/", "\\")
            category_list.append(category)

        categories = resp.xpath(silo_li)[2]
        href_list = categories.xpath('.//ul//a/@href').extract()
        for href in href_list:
            href_all_list.append(href)
            cat2 = extract_var(href, r"en-jp/(.*?)/cat")
            category = cat0 + "\\" + str(cat2).replace("/", "\\")
            category_list.append(category)

        # NM Kids
        cat0 = "Kids"
        silo_li = '//li[@id="silo9"]//div[@class="silo-column"]'
        categories = resp.xpath(silo_li)[0]
        ul_list = categories.xpath('.//ul')[0]
        href_list = ul_list.xpath('.//a/@href').extract()
        for href in href_list:
            href_all_list.append(href)
            cat2 = extract_var(href, r"en-jp/(.*?)/cat")
            category = cat0 + "\\" + str(cat2).replace("/", "\\")
            category_list.append(category)

        categories = resp.xpath(silo_li)[1]
        href_list = categories.xpath('.//ul//a/@href').extract()
        for href in href_list:
            href_all_list.append(href)
            cat2 = extract_var(href, r"en-jp/(.*?)/cat")
            category = cat0 + "\\" + str(cat2).replace("/", "\\")
            category_list.append(category)
        categories = resp.xpath(silo_li)[2]
        href_list = categories.xpath('.//ul//a/@href').extract()
        for href in href_list:
            href_all_list.append(href)
            cat2 = extract_var(href, r"en-jp/(.*?)/cat")
            category = cat0 + "\\" + str(cat2).replace("/", "\\")
            category_list.append(category)
        href_list = categories.xpath('.//h6//a/@href').extract()
        href_all_list.append(href_list[1])
        cat2 = extract_var(href_list[1], r"Kids/(.*?)/cat")
        category = cat0 + "\\" + str(cat2).replace("/", "\\")
        category_list.append(category)

        # Home
        cat0 = "Home"
        silo_li = '//li[@id="silo10"]//div[@class="silo-column"]'
        categories = resp.xpath(silo_li)[1]
        href_list = categories.xpath('.//ul//a/@href').extract()
        for href in href_list:
            href_all_list.append(href)
            cat2 = extract_var(href, r"en-jp/(.*?)/cat")
            category = cat0 + "\\" + str(cat2).replace("/", "\\")
            category_list.append(category)

        categories = resp.xpath(silo_li)[2]
        list = [0, 1, 2]
        for i in list:
            ul_list = categories.xpath('.//ul')[i]
            href_list = ul_list.xpath('.//a/@href').extract()
            for href in href_list:
                href_all_list.append(href)
                cat2 = extract_var(href, r"en-jp/(.*?)/cat")
                category = cat0 + "\\" + str(cat2).replace("/", "\\")
                category_list.append(category)
        href_list = categories.xpath('.//h6//a/@href').extract()
        list = [2, 3, 4, 6, 7]
        for i in list:
            href_all_list.append(href_list[i])
            cat2 = extract_var(href_list[i], r"en-jp/(.*?)/cat")
            category = str(cat2).replace("/", "\\")
            category_list.append(category)
        for href, cat in zip(href_all_list, category_list):
            TestModels.add_cat_info(href, cat)

    def parse_categorylink(self, response):
        if response.meta['type'] == 2:
            json_data = json.loads(response.body)
            sel = Selector(text=json_data.get('GenericSearchResp', '').get('productResults', ''))
            numItems = [0]
        else:
            navLastItem = response.xpath('//a[contains(@class,"navLastItem")]/@href').extract()
            numItems = response.xpath('//span[@id="numItems"]/text()').extract()
        if len(numItems) > 0:
            items_count = response.meta['items_count']
            find_count = response.meta['find_count']
            page_num = response.meta['page_num']
            if int(response.meta['type']) == 0:
                items_count = int(numItems[0])
                self.all_count += items_count
                find_count = 0
                page_num = 0
            if response.meta['type'] == 2:
                productList = sel.xpath('//a[@id="productTemplateId"]/@href').extract()
            else:
                productList = response.xpath('//a[@id="productTemplateId"]/@href').extract()
            for href in productList:
                url = self.base_url + href
                find_count += 1
                yield scrapy.Request(url=url, callback=self.parse_product,
                                     meta={'data': url, 'cat': response.meta['cat']})
            if find_count < items_count and page_num * self.page_size <= items_count:
                page_num += 1
                catId = 'cat' + str(re.search(r"\/cat(.*?)_cat", response.meta['url1']).groups()[0])
                tmp = '{"GenericSearchReq":{"pageOffset":' + str(page_num) + ',"pageSize":"' + str(self.page_size) \
                      + '","refinements":"","selectedRecentSize":"","activeFavoriteSizesCount":"0","activeInteraction":"true","mobile":false,' \
                        '"sort":"PCS_SORT","personalizedPriorityProdId":"","endecaDrivenSiloRefinements":"pageSize=120","definitionPath":"/nm/commerce/pagedef_rwd/template/EndecaDrivenHome",' \
                        '"userConstrainedResults":"true","updateFilter":"false","rwd":"true","advancedFilterReqItems":{"StoreLocationFilterReq":[{"allStoresInput":"false","onlineOnly":""}]},' \
                        '"categoryId":"' + catId + '","sortByFavorites":false,"isFeaturedSort":false,"prevSort":""}}'
                tmp1 = "$b64$" + base64.b64encode(tmp)
                data = tmp1.replace("=", "$")
                post_url = self.base_url + "/en-jp/category.service"
                timestamp = str(time.time() * 1000)
                formdata = {'data': data,
                            'service': 'getCategoryGrid',
                            'sid': 'getCategoryGrid',
                            'bid': 'GenericSearchReq',
                            'timestamp': timestamp}
                yield FormRequest(url=post_url, formdata=formdata, callback=self.parse_categorylink,
                                  meta={'type': 2, 'url1': response.meta['url1'], 'items_count': items_count,
                                        'find_count': find_count, 'page_num': page_num, 'cat': response.meta['cat']})
        else:
            if len(navLastItem) > 0:
                pageSize = '?pageSize=' + str(self.page_size)
                for href in navLastItem:
                    url = self.base_url + href + pageSize
                    url1 = self.base_url + href
                    yield scrapy.Request(url=url, callback=self.parse_categorylink,
                                         meta={'type': 0, 'url1': url1, 'items_count': 0, 'find_count': 0,
                                               'page_num': 0, 'cat': response.meta['cat']})

    def parse_product(self, response):
        self.fail_count += 1


        def extract_var(reg):
            return response.xpath('//script').re(reg)

        prodURL = response.meta['data'].encode('shift_jis')

        prodInfo = json.loads((extract_var(r"window.utag_data=(.*?);\n"))[0])
        productId = (prodInfo["product_id"])[0]
        prod_info = TestModels.get_prod_info(str(productId))
        if prod_info != None:
            return
        # get product other detail info
        product_name = (prodInfo["product_name"])[0].encode('utf-8')
        categoryId = (prodInfo["cat_id"])[len(prodInfo["cat_id"]) - 1]
        category_set_num = int(re.search('\d+', categoryId).group())
        price = float((prodInfo["product_price"])[0])
        exchangeRate = float((extract_var(r"var exchangeRate = (.*?);"))[0])
        # prodPrice = format(round(price * exchangeRate), ",.2f")
        # prodPrice = round(price * exchangeRate)
        prodPrice = round(price)
        brand_span = response.xpath('//span[contains(@class, "product-designer")]')
        if len(brand_span) > 0:
            brandEle = brand_span[0]
            if len(brandEle.xpath('.//a')) > 0:
                brand_name = brandEle.xpath('.//a/text()').extract()[0].encode('shift_jis')
            else:
                brand_name = brandEle.css('::text').extract()[0].encode('shift_jis')
        else:
            brand_name = ''


        categoryList = response.meta['cat']
        category_name = categoryList
        category_set_name = (categoryList.split("\\")[0]).encode('shift_jis')

        TestModels.add_prod_info(productId, category_name, str(time.strftime("%Y-%m-%d")))


        prodImgURL = (response.xpath('//div[@class="img-wrap"]//img/@src').extract()[0]).encode('shift_jis')

        # get product description
        prodDescription = ''
        prodDetailList = response.xpath('//div[@class="productCutline"]')
        if len(prodDetailList) > 0:
            prodInfoList = prodDetailList[0].xpath('.//li')
            if len(prodInfoList) < 1:
                prodInfoList = prodDetailList[0].xpath('.//div')
            for i in range(len(prodInfoList)):
                text_in_li = prodInfoList[i].css('::text, *::text').extract()
                for j in range(len(text_in_li)):
                    str_one = text_in_li[j].encode('utf-8')
                    if str_one.strip():
                        prodDescription = prodDescription + str_one
                    else:
                        prodDescription = prodDescription + " "
                if i < len(prodInfoList) - 1:
                    prodDescription = prodDescription + '\n\r'

        aboutDesignerList = response.xpath('//div[@class="aboutDesignerCopy"]')
        if len(aboutDesignerList) > 0:
            if prodDescription.strip():
                prodDescription = prodDescription + '\n\r\n\r'
            list = aboutDesignerList[0].css('::text').extract()
            print(len(list))
            for k in range(len(list)):
                if k < len(list) - 1:
                    prodDescription = prodDescription + list[k].encode('utf-8') + "\n\r"
                else:
                    prodDescription = prodDescription + list[k].encode('utf-8')
        # check shipable product
        ship_error = False
        error_text = ""
        error_text_list = response.xpath('//p[@class="error-text"]')
        if len(error_text_list) > 0:
            error_text = error_text_list[0].xpath('./text()').extract()[0]
            if "We are sorry" in error_text:
                ship_error = True
        if str((prodInfo["product_available"])[0]) == "true" and not ship_error:
            # get product balance and color type
            req_url = "http://www.neimanmarcus.com/en-jp/product.service"
            tmp = '{"ProductSizeAndColor":{"productIds":"' + str(productId) + '"}}'
            tmp1 = "$b64$" + base64.b64encode(tmp)
            data = tmp1.replace("=", "$")
            timestamp = str(time.time() * 1000)
            request_data = {
                "data": data,
                "sid": "getSizeAndColorData",
                "bid": "ProductSizeAndColor",
                "timestamp": timestamp,
            }

            yield FormRequest(url=req_url, formdata=request_data, callback=self.parse_detail_product,
                              meta={'productId': productId,
                                    'product_name': product_name,
                                    'category_name': category_name,
                                    'prodURL': prodURL,
                                    'category_set_num': category_set_num,
                                    'category_set_name': category_set_name,
                                    'brand_name': brand_name,
                                    'prodPrice': prodPrice,
                                    'prodDescription': prodDescription,
                                    'prodImgURL': prodImgURL
                                    })

    def parse_detail_product(self, response):
        json_data = json.loads(response.body)
        res1 = json.loads(json_data['ProductSizeAndColor']['productSizeAndColorJSON'])

        productId = response.meta['productId']

        sel_type = ''
        # add information in select.csv
        skusList = res1[0]['skus']
        select_list = []
        size_count = 0
        size_list = []
        color_count = 0
        color_list = []
        sc_count = 0
        for m in range(len(skusList)):
            sel1 = u'カラー'.encode('shift_jis')
            sel2 = u'カラー'.encode('shift_jis')
            if 'stockLevel' in skusList[m]:
                sel_balance = int(skusList[m]['stockLevel'])
            else:
                sel_balance = int(skusList[m]['stockAvailable'])
            if sel_balance == 0:
                sel_balance = 999
            if 'size' in skusList[m]:
                if skusList[m]['size'] != None and skusList[m]['size'].upper() != "NO SIZE":
                    sel_type = 'i'
                    sel1 = (skusList[m]['size']).encode('shift_jis')
                    if 'color' in skusList[m]:
                        sel2 = (skusList[m]['color']).encode('shift_jis').split("?")[0]
                    sel_row = ['n', productId, sel_type, '', '', sel1, '', sel2, '', '1', sel_balance, '1', '1', 4, 5,
                               '', '']

                    sc_count += 1
                    if sel1.upper() not in size_list:
                        size_count += 1
                        size_list.append(sel1.upper())
                    if sel2.upper() not in color_list:
                        color_count += 1
                        color_list.append(sel2.upper())
                else:
                    if len(skusList) > 1:
                        sel_type = 's'
                    else:
                        sel_type = 'c'
                    if 'color' in skusList[m]:
                        sel1 = (skusList[m]['color']).encode('shift_jis').split("?")[0]
                    sel_row = ['n', productId, sel_type, u'カラー'.encode('shift_jis'), sel1, '', '', '', '', '', '', '',
                               '', '', '', '', '']
            else:
                if len(skusList) > 1:
                    sel_type = 's'
                else:
                    sel_type = 'c'
                if 'color' in skusList[m]:
                    sel1 = (skusList[m]['color']).encode('shift_jis').split("?")[0]
                sel_row = ['n', productId, sel_type, u'カラー'.encode('shift_jis'), sel1, '', '', '', '', '', '',
                           '', '', '', '', '', '']
            select_list.append(sel_row)

        if sc_count != 0 and (sc_count != (size_count * color_count) or sc_count != len(skusList)):
            return

        selColor = ''
        if 'color' in (res1)[0]['skus'][0]:
            selColor = ((res1)[0]['skus'][0]['color']).encode('shift_jis').split("?")[0]
        str_balance = ''
        if sel_type != 'i':
            str_balance = str((res1)[0]['skus'][0]['stockAvailable'])
            if str_balance == '0':
                str_balance = '999'
        # end

        item = WebscraperDemoItem()

        item['balance'] = str_balance
        item['selType'] = sel_type
        item['selectedColor'] = selColor
        item['productId'] = productId
        item['product_name'] = response.meta['product_name']
        item['category_name'] = response.meta['category_name']
        item['prodURL'] = response.meta['prodURL']
        item['category_set_num'] = response.meta['category_set_num']
        item['category_set_name'] = response.meta['category_set_name']
        item['brand_name'] = response.meta['brand_name']
        item['price'] = response.meta['prodPrice']
        item['prodDescription'] = response.meta['prodDescription']
        item['select_list'] = select_list

        img_url = response.meta['prodImgURL']
        if 'http:' not in img_url:
            if '//' in img_url:
                img_url = 'http:' + img_url
            else:
                img_url = self.base_url + img_url
        # thumb_guid = hashlib.sha1(to_bytes(img_url)).hexdigest()


        # customizing the product foler and image url by me
        self.product_image_count += 1
        # print ('product image count is ' + self.product_image_count)
        if self.product_image_count == 2001:
            self.product_image_count = 0
            self.product_folder_count += 1
            self.folder_insert_result = self.cabinet_foler_insert('nei_man'+self.product_folder_count)
        if self.folder_insert_result is not 'error':
            thumb_guid = str(productId)+'.jpg'
            self.image_result = self.cabinet_file_insert(thumb_guid, self.folder_insert_result)
        if self.image_result == 'success':
            thumb_guid = str(productId)
            img_path = const.IMAGE_UPLOAD_PATH+'/nei_man'+self.product_folder_count
            item['prodImgURL'] = '%s%s.jpg' % (img_path, thumb_guid)
        elif self.image_result == 'error':
            item['prodImgURL'] = ''
        #  end customizing item['prodImgURL']


        # thumb_guid = str(productId)
        # img_path = const.IMAGE_UPLOAD_PATH+'/'
        # item['prodImgURL'] = '%s%s.jpg' % (img_path, thumb_guid)
        item['image_urls'] = [img_url]

        self.fail_count -= 1
        self.find_count += 1
        item['all_product_count'] = self.all_count
        item['find_product_count'] = self.find_count
        item['fail_product_count'] = self.fail_count
        yield item

    # sending web service
    def send_web_service(self, url, xml, header):
        result = requests.post(url, data=xml, headers=header).text
        return result
        print (result)

    # making xml file
    def make_xml(self, xml_data):
        xml = dicttoxml.dicttoxml(xml_data, custom_root='request', attr_type=False)
        return xml

    # inserting product image foldfer per 2000 units
    def cabinet_foler_insert(self,folder_name):
        url = 'https://api.rms.rakuten.co.jp/es/1.0/cabinet/folder/insert'
        header = {
            'Authorization': 'ESA Base64 (serviceSecret : licenseKey)'
        }
        xml_data = {
            'folderInsertRequest': {
                'folder': {
                    'folderName': folder_name
                }
            }
        }
        xml = self.make_xml(xml_data)
        response_xml = self.send_web_service(url, xml_data, header)
        root = ET.fromstring(response_xml)
        systemStatus = ''
        FolderId = ''
        # getting FolderId
        for elem in root.iter():
            if elem.tag == 'systemStatus':
                systemStatus = elem.text
                print(systemStatus)
            elif elem.tag == 'FolderId':
                FolderId = elem.text
                print(FolderId)
        if systemStatus == 'OK' and FolderId is not '':
            return FolderId
            print('Image folderid  is '+FolderId)
        else:
            return 'error'
            print('Inserting folder Error')
    # inserting the product image into the folder
    def cabinet_file_insert(self,image_name, folder_id):
        BASE_DIR_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        RESULT_DIR_PATH = os.path.join(BASE_DIR_PATH, 'result')
        IMAGE_PATH = os.path.join(RESULT_DIR_PATH, "img")
        url = 'https://api.rms.rakuten.co.jp/es/1.0/cabinet/file/insert'
        header = {
            'Authorization': 'ESA Base64 (serviceSecret : licenseKey)',
            'Content-Type': 'multipart/form-data'
        }
        xml_data = {
            'fileInsertRequest': {
                'file': {
                    'fileName': image_name,
                    'folderId': folder_id,
                    'filePath': IMAGE_PATH + '/' + image_name,
                    'overWrite': 'true'
                }
            }
        }
        xml = self.make_xml(xml_data)
        response_xml = self.send_web_service(url, xml_data, header)
        root = ET.fromstring(response_xml)
        systemStatus = ''
        FileId = ''
        # getting FolderId
        for elem in root.iter():
            if elem.tag == 'systemStatus':
                systemStatus = elem.text
                # print(systemStatus)
            elif elem.tag == 'FileId':
                FileId = elem.text
                # print(FileId)
        if systemStatus == 'OK' and FileId is not '':
            return 'success'
            print('product image url is '+FileId)
        else:
            return 'error'
            print('Inserting folder Error')

