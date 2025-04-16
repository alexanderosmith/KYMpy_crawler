# EXAMPLE/SCRATCH FILE FOR BUILDING AN IMAGE COLLECTOR WITH SCRAPY
# AUTHOR: Alexander O. Smith
#################################################################################
# Imports #######################################################################
#%pip install pillow
import sys, os, json, logging, scrapy
os.chdir('/home/aos11409/Documents/000_PhD_Files/000_Projects/GoogleVisionProject/KYM_Scrapy_Proj')
os.getcwd()
from scrapy.spiders import CrawlSpider, Rule, Request
from scrapy.linkextractors import LinkExtractor                                  # LinkExtractor enables following links of a specific pattern
from scrapy.pipelines.images import ImagesPipeline
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
sys.path.append('KYM_spider/KYM_spider')
#os.getcwd()
#os.listdir(itmloc)
from items import ImageItem
from PIL import Image
#################################################################################
# EXAMPLES ######################################################################
#################################################################################

class KYM_img(scrapy.Spider):
    name = 'KYM_img'
    allowed_domains = ['knowyourmeme.com/', 'i.kym-cdn.com']
    start_urls = ['https://knowyourmeme.com/photos/1370340-netflix']


    headers =  {                                                                            # Tell website I am a Chrome browser
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
                                                                                            # Update the user-agent occasionally
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.165 Safari/537.36'
        }
    
    custom_settings = {                                                                     # Use scrapy automated throttling
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_DEBUG': True
    }
    
    Rule(LinkExtractor(
        allow=('.jpg')              # Allows jpg extension
        , deny_extensions=set()     # Empties default deny_extension
        , tags = ('img')            # Tags which are img
        , attrs=('src')
        , canonicalize = True
        , unique = True)
        , follow = False
        , callback='parse_item'
    )

    # Enable Image Scraping (For documentation on media pipelines and storage: https://docs.scrapy.org/en/latest/topics/media-pipeline.html )
    ITEM_PIPELINES = {'scrapy.pipelines.images.ImagesPipeline': 1}                          # Image pipeline (this is directly from scrapy docs)
    # Save Location
    IMAGES_STORE = './ImgScrapeEx'  
    
    def parse(self, response):
        self.log('A response from %s just arrived!' % response.url)                                                       # Image storage location

    def parse_item(self, response):
            self.logger.info('Found image - %s', response.url)
            with open('image_ex.jpg', 'wb') as html_file:
                html_file.write(response.body)

            #self.logger.info('Saved image as - %s', flname)
            item = scrapy.Item()
            return item

# NotImplementedError: KYM_img.parse callback is not defined
# This particular class needs a parse call which is not defined. 
# Look at examples of this and see how to write it in this example. 
