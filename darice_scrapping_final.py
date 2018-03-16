#!/usr/bin/python 2.7
# -*- coding: utf-8 -*-

import requests
from lxml import html
import pickle
import pandas as pd

class Parsing():
    
    def __init__(self):
        self.items = []
        self.main_images = []
        self.upcs = []
        self.prices = []
        self.casepacks = []
        self.innerpacks = []
        self.instocks = []
        self.colors = []
        self.shapes = []
        self.description = []
        self.names = []
        self.pages = []
        self.all_pages = []
        self.all_links = []
        self.categories = []
        
    def get_allpages(self, url): 
        try:
            self.get_url(url)
            scroll_link =  tree.xpath('//a[@id="pagingShowMore"]')
            #print len(scroll_link)
            if scroll_link:
                next_link = '{}{}'.format('https://www.darice.com',scroll_link[0].get('href'))
                print (next_link)
                if url not in self.all_pages:
                    self.all_pages.append(url)
                    self.get_allpages(next_link)
            else:
                print ('no scroll page')
                if url not in self.all_pages:
                    self.all_pages.append(url)
        except Exception as e:
            print (e)
    
    def get_allinks(self, url):
        try:
            self.get_url(url)
            links = [n for n in tree.xpath('//a[@class="boldLink productLink"]')]
            for n in links:
                lnk = '{}{}'.format('https://www.darice.com', n.get('href'))
                if lnk not in self.all_links:
                    self.all_links.append(lnk)
        except Exception as e:
            print ('links not found')
    
    def get_categories(self, url):
        try:
            self.get_url(url)
            category = [n.get('href') 
                        for n in tree.xpath('//div[@class="containerMargin10"]/ul/li/ul/li/a') 
                        if '/catalog/' in n.get('href')]  
            for url in category:
                print (url)
                self.categories.append(url)   
        except Exception as e:
            print e


    def get_pages(self, url):
        try:
            self.get_url(url)
            listing =  [n.get('href') 
                        for n in
                        tree.xpath('//div[@class="categoryListing"]//h3/a')]
            if listing:
                for i in listing:
                    url = '{}{}'.format('https://www.darice.com', i)
                    print url
                    self.get_pages(url)
            else:
                print (url) 
                print ('no category page')
                self.pages.append(url)
                #print self.categories
        except Exception as e:
            print e

    def get_url(self, url):
        try:
            headers = {"Connection" : "close",'User-Agent':'Opera/9.80 \
                       (Windows NT 5.2; U; ru) Presto/2.7.62 Version/11.01'}
            root = requests.get(url, headers=headers)
            global tree
            tree = html.fromstring(root.content)
            #print html.tostring(tree)
        except Exception as e:
            print e
            print 'failed to get url: ', url

    def get_field(self, field_name, field_list):
        try:
            field = [n.getnext().text_content() for n in 
            tree.xpath('//span[@class="alignLeft"]') 
            if field_name in n.text_content()]
            #print field[0].strip()
            field_list.append(field[0].strip())
        except Exception as e: 
            print e
            field_list.append('')

    def get_name(self):
        try:
            field = [n.text_content().encode('utf-8') for n in 
            tree.xpath('//div[@id="specifications"]/h3')]
            #print field[0].strip()
            self.names.append(field[0].strip())
        except Exception as e: 
            print e
            self.names.append('')
    
    def get_mainimage(self):
        try:
            image = [n.get("src") for n in 
            tree.xpath('//div[@class="jsProductDetailImage"]/img')]
            #print image[0]
            self.main_images.append(image[0])
        except Exception as e: 
            print e
            self.main_images.append('')


    def get_description(self):
        try:
            descr = [n.text_content() for n in 
            tree.xpath('//div[@id="description"]')]
            if "This item" in descr[0]:
                #print descr[0].split("This item")[0].encode('utf-8').strip()
                self.description.append(descr[0].split("This item")[0].encode('utf-8').strip())
            else:
                #print descr[0].split('View Full')[0].encode('utf-8').strip()
                self.description.append(descr[0].split('View Full')[0].encode('utf-8').strip())
        except Exception as e: 
            print e
            self.description.append('')


def main():
    site_map = 'https://www.darice.com/home/sitemap'
    new = Parsing()

    new.get_categories(site_map)

    for url in new.categories:
        new.get_pages(url)

    for url in new.pages:
        new.get_allpages(url)

    count = 0
    for url in new.all_pages:
        new.get_allinks(url)
        count+=1
        print ('{} links have been found'.format(count))

    fields = {
               'Item #':new.items, 'UPC #':new.upcs,
               'Your Price': new.prices, 'Case Pack': new.casepacks,
               'Inner Pack': new.innerpacks, 'In Stock': new.instocks,
               'Color': new.colors, 'Shape': new.shapes
                  }

    count = 0
    for url in new.all_links: 
        new.get_url(url)
        new.get_name()
        for field_name, field_list in fields.iteritems(): # dict.items() for python 3
            new.get_field(field_name, field_list)
        new.get_mainimage()
        #print new.main_images
        new.get_description()
        count+=1
        print("{} links out of {} have been scrapped ".format(count,len(new.all_links)))

    df = pd.DataFrame({"item": new.items,
                       "main_image":new.main_images,
                       "product_name": new.names,
                       "upc": new.upcs,
                       "price": new.prices,
                       "case_pack": new.casepacks,
                       "inner_pack": new.innerpacks,
                       "in_stock" : new.instocks,
                       "color": new.colors,
                       "shape": new.shapes, 
                       "description": new.description
                           },
                       columns=["item","product_name",
                       "main_image", "upc","price", 
                       "case_pack", "inner_pack", "in_stock", 
                       "color", "shape","description"])

    df.to_csv('darice_all.csv', encoding='utf-8', index=False)

    pickling_on = open("darice_df.pickle","wb")
    pickle.dump(df, pickling_on)
    pickling_on.close()

if __name__ == '__main__':
    main()