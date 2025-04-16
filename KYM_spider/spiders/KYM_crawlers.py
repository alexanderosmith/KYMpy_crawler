#################################################################################
# Know Your Meme Crawlers:
# Author: Alexander O. Smith
# Created: 12/23/2022
# Updated: 12/31/2022
#################################################################################
# Crawler Names, Definitions, and Brief Documentation ###########################
# 1. KYM_entry: gathers meme entry names, number, labels, and links of ~/page/1. 
# 2. KYM_entry_scroller: KYM_entry for all pages of KYM via infinite scroll. 
# 3. KYM_img_crawl: collects image (meta)data for a particular KYM entry.
#################################################################################
#/* cSpell:disable */
# This is a script which uses scrapy in order to crawl Know Your Meme. The
# crawlers in this script are meant to collect images and their metadata for my
# dissertation project. However, eventually, they may be developed into more
# general scripts for data collection in bigger projects.
#################################################################################
# Imports #######################################################################
#%pip install pillow
import sys, os, json, logging, scrapy, re
os.chdir('/home/aos11409/Documents/000_PhD_Files/000_Projects/GoogleVisionProject/KYM_Scrapy_Proj')
os.getcwd()
from scrapy.spiders import CrawlSpider, Rule, Request
from scrapy.linkextractors import LinkExtractor                                  # LinkExtractor enables following links of a specific pattern
from scrapy.pipelines.images import ImagesPipeline
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
sys.path.append('KYM_spider/KYM_spider')
sys.path.insert(0,'./KYM_spider') # Tells python where items.py is for import.
from items import ImageItem # This needs to be changed to route to items.py
from items import ImageItem
from PIL import Image

# Following Scrapy Class from: #############################################################
# https://www.accordbox.com/blog/how-crawl-infinite-scrolling-pages-using-python/
# You're going to have to go through this and document what it does more clearly.
############################################################################################
# This works, but does not scroll. 
# DO NOT EDIT!!!!!!! Use this to debug.

class KYM_test(scrapy.Spider):
    name = 'KYM_pg1'
    allowed_domains = ['knowyourmeme.com/memes/all']
    start_urls = ['https://knowyourmeme.com/memes/all/page/1']

    def parse(self, response):
        for entry in response.xpath("//tbody[@class='entry-grid-body infinite']//td[@class]"):
            yield {
                # Name of each KYM entry
                'entry_name': entry.xpath('.//h2[1]/a/text()').get(),
                # The entry number in the str format entry_<number>
                'entry_num': entry.xpath('./@class').get(),
                # The KYM classifications of each entry
                'entry_labels': entry.xpath(".//div[@class='entry-labels']/span/text()").getall(),
                # The first URL to the entry listed
                'entry_link': response.urljoin(entry.xpath("./a[@href]/@href").get())
            }
class KYM_entrys(scrapy.Spider):
    name = 'KYM_entry_scroller'
    allowed_domains = ['knowyourmeme.com']
    #start_urls = ['https://knowyourmeme.com/memes/all/page/1']

    headers =  {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }
    
    custom_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_DEBUG': True
    }

    def start_requests(self):
        yield Request(
            url="https://knowyourmeme.com/memes/all/page/1",
            callback=self.parse_list_page
        )

    def parse_list_page(self, response):
        
        """
        The url of next page is like
        https://scrapingclub.com/exercise/list_infinite_scroll/?page=2

        It can be found in an xpath that looks like:
        //section/aside/div/div/a[@rel='next']
        """

        #First, check if next page available, if found, yield request
        next_link = response.xpath(
            "//section/aside/div/div/a[@rel='next']/@href"
            ).extract_first()
        if next_link:
            # If the website has strict policy, you should do more work here
            # Such as modifying HTTP headers

            # concatenate url
            url = response.url
            print(url)
            # This concat needs fixin'
            next_link = response.urljoin(next_link)
            yield Request(
                url=next_link,
                callback=self.parse_list_page   
            )
            

        # Find Meme Entry Data and Yield Request
        for req in self.entry_parse(response):
            yield req

    def entry_parse(self, response):
        for entry in response.xpath("//tbody[@class='entry-grid-body infinite']//td[@class]"):
            yield {
                # Name of each KYM entry
                'entry_name': entry.xpath('.//h2[1]/a/text()').get(),
                # The entry number in the str format entry_<number>
                'entryID': entry.xpath('./@class').get(),
                # The KYM classifications of each entry
                'entry_labels': json.dumps(
                    entry.xpath(".//div[@class='entry-labels']/span/text()").getall()
                    , separators=("|", ":")),
                # The first URL to the entry listed
                'entry_link': response.urljoin(entry.xpath("./a[@href]/@href").get())
            }

# Header Info from KYM
# User-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36
# X-Requested-With: XMLHttpRequest
# Referrer: https://knowyourmeme.com/memes/all/page/1

############################################################################################
class img_md(scrapy.Spider):
    name = 'KYM_img_metadata'
    allowed_domains = ['knowyourmeme.com', 'i.kym-cdn.com']
    def __init__(self, meme='rickroll', **kwargs):
        global meme_url
        meme_clean = re.sub('[^A-Za-z0-9 ]', '', meme)
        meme_url = re.sub(' ', '-', meme_clean).lower()
        self.start_urls = [f'https://knowyourmeme.com/memes/{meme_url}/photos']
        super().__init__(**kwargs)

    #example start_urls = ['https://knowyourmeme.com/memes/you-like-krabby-patties-dont-you-squidward/photos']

#    rules = ( # This should work bc it works in 'example_img' scraper.
#        # This rule set removes the deny_extensions default setting 
#        Rule(LinkExtractor(deny_extensions=set(), tags = ('img',), attrs=('src',), canonicalize = True, unique = True), follow = False, callback='parse_item'),
#    )


# Initiates the scrape
    def start_requests(self):
        yield Request(
            url=f'https://knowyourmeme.com/memes/{meme_url}/photos',
            callback=self.parse_list_page # Activates infinite scroll page search
        )

# Returns the full page list in an infinite scroll
    def parse_list_page(self, response):
        #First, check if next page available, if found, yield request
        next_link = response.xpath(
            "//a[@rel='next']/@href"
            ).extract_first()
        print('NEXT LINK: '+str(next_link))
        if next_link:
            # If the website has strict policy, you should do more work here
            # Such as modifying HTTP headers

            # concatenate url
            url = response.url
            print(url)

            next_link = response.urljoin(next_link)
            yield Request(
                url=next_link,
                callback=self.parse_list_page
            )
            

        # Initiate Parse Function
        for req in self.parse(response):
            yield req

# Returns the hrefs of image page in the gallery
    def parse(self, response):
        for link in response.xpath("//div[@class='infinite']/div/a/@href").getall():
            print('''

            HERE IS THE LINK:'''+str(link)+'''
            
            ''')

# How does this next step work?
            # For each link, follow link with parse_img
            #print('Link: ' + link)
            
            # I need to figure out how to parse image and parse metadata
            #yield response.follow(link, callback=self.parse_img),
            yield response.follow(link, callback=self.parse_metadata)

# Returns Image Level Metadata
    def parse_metadata(self, response):
        vote = response.xpath("//header/div[@class='thumb_mini_container']//span[@title]")
        fave = response.xpath("/html/body/div[3]/div/div[2]/header/div[1]")
        img = response.xpath("//aside[@class='right']")
        favorites = fave.xpath(".//a/span[@class='num']/text()").get()
        votes = vote.xpath('./@title').get().split(' up, ')
        up_votes = votes[0]
        down_votes = votes[1].split(' ')[0]
        view_count = img.xpath(".//span[@class='view_count']/text()").get()
        date_posted = img.xpath(".//abbr[@class='timeago']/@title").get()
        origin_entry = img.xpath(".//a[@class='origin-entry-summary']/text()").get()
        tags = img.xpath(".//p[@id='tag_list']/a/text()").getall()
        uploader = img.xpath(".//div[@class='sidebar_box grey c']//div[@class='name left']/h6/a/text()").get()
        if uploader == None:
            uploader = img.xpath(".//div[@class='sidebar_box grey c']//div[@class='name left']/h6/text()").get()
        uploader_role = img.xpath(".//div[@class='sidebar_box grey c']//div[@class='name left']/p[@class='role']/text()").get()
        if uploader_role == None:
            uploader_role = img.xpath(".//div[@class='sidebar_box grey c']//div[@class='name left']/p[@class='role']/a/text()").get()
        uploader_profile = img.xpath(".//div[@class='sidebar_box grey c']//div[@class='name left']/h6/a/@href").get()
        if uploader_profile == None:
            uploader_profile = img.xpath(".//div[@class='sidebar_box grey c']//div[@class='name left']/h6/@href").get()
        # Check notes to see whether 'row expandable media-notes' class needs modification to contains()
        notes = img.xpath("//aside[@class='right']//div[@class='row expandable media-notes']").getall()
        source = img.xpath(".//p//span[@style]/text()").get()
        img_id = 'img_'+img.xpath(".//textarea/@id").get().split('_')[-1]
        embedded_img_link = img.xpath(".//textarea/text()").get()
        link = str(response).split()[1].split('>')[0]

        yield {
            'img_id': img_id,
            'favorites': favorites,
            'up_votes': up_votes,
            'down_votes': down_votes,
            'view_count': view_count,
            'date_posted': date_posted,
            'origin_entry': origin_entry,
            'notes': notes,
            'tags': tags,
            'uploader': uploader.strip(),
            'uploader_role': uploader_role.strip(),
            'uploader_profile': uploader_profile,
            'source': source,
            'link': link,
            'embedded_img_link': embedded_img_link,
        }

class imgs(scrapy.Spider):
    name = 'KYM_imgs'
    allowed_domains = ['knowyourmeme.com', 'i.kym-cdn.com']

    def __init__(self, meme='rickroll', **kwargs):
        global meme_url
        meme_clean = re.sub('[^A-Za-z0-9 ]', '', meme)
        meme_url = re.sub(' ', '-', meme_clean).lower()
        self.start_urls = [f'https://knowyourmeme.com/memes/{meme_url}/photos']
        super().__init__(**kwargs)

    custom_settings = {
        'ITEM_PIPELINES': {'KYM_spider.pipelines.ImgIDPipeline': 1},
        'IMAGES_STORE': 'images/garfielf'
    }
    
    rules = ( # This should work bc it works in 'example_img' scraper.
        # This rule set makes sure it downloads anything with the extension .jpg in it and also removes the deny_extensions default setting 
        Rule(LinkExtractor(
            allow=('.png', '.jpg', '.jpeg'), 
            deny_extensions=set(), 
            tags = ('img',), 
            attrs=('src',), 
            canonicalize = True, 
            unique = True), 
            follow = False, 
            callback='parse_item'),
    )

# Initiates the scrape
    def start_requests(self):
        yield Request(
            url=f'https://knowyourmeme.com/memes/{meme_url}/photos',
            callback=self.parse_list_page # Activates infinite scroll page search
        )

# Returns the full page list in an infinite scroll
    def parse_list_page(self, response):
        #First, check if next page available, if found, yield request
        next_link = response.xpath(
            "//a[@rel='next']/@href"
            ).extract_first()
        print('NEXT LINK: '+str(next_link))
        if next_link:
            # If the website has strict policy, you should do more work here
            # Such as modifying HTTP headers

            # concatenate url
            url = response.url
            print(url)

            next_link = response.urljoin(next_link)
            yield Request(
                url=next_link,
                callback=self.parse_list_page
            )
            

        # Initiate Parse Function
        for req in self.parse(response):
            yield req

# Returns the hrefs of image page in the gallery
    def parse(self, response):
        for link in response.xpath("//div[@class='infinite']/div/a/@href").getall():

            yield response.follow(link, callback=self.parse_img)

# Returns Image Files
    def parse_img(self, response):
        print("Parsing Image")
        item = ImageItem()
        if response.status == 200:
            img_links = []
            for img in response.xpath("//div[@id='photo_wrapper']//img/@src").extract():
                img_links.append(img)
            item['image_urls'] = self.url_join(img_links, response)
        return item

    def url_join(self, img_links, response):
        joined_urls = []
        for rel_img_url in img_links:
            joined_urls.append(response.urljoin(rel_img_url))
        return joined_urls
    
# To run "scrapy crawl KYM_img_crawl -o KYMimg_url_ex.csv"

class imgs(scrapy.Spider):
    name = 'KYM_leaderboard'
    allowed_domains = ['knowyourmeme.com', 'i.kym-cdn.com']
    start_urls = ['https://knowyourmeme.com/user-leaderboards/videos/all-time']

    custom_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_DEBUG': True,
        'ROBOTSTXT_OBEY': False
    }

    def start_requests(self):
        yield Request(
            url=f'https://knowyourmeme.com/user-leaderboards/videos/all-time',
            callback=self.parse_users # Activates infinite scroll page search
        )
    
    def parse_users(self, response):
        for link in response.xpath("//td[@class='user']//a/@href").getall()[:2]:
            print('''
            THE USER PROFILE IS AT '''+str(link)+'''
            
            ''')

            yield response.follow(link, callback=self.parse_user_md)

    def parse_user_md(self, response):
        for user in response.xpath('.'):
            profile = user.xpath("//div[@id='profile_bio']/h1/text()").get()
            role = user.xpath("//div[@id='profile_bio']/h5/text()").get()
            location = user.xpath("//div[@id='profile_bio']/p[1]/text()").get()
            joined = user.xpath("//p/abbr/@title").get()
            about = user.xpath("//dl//p/text()").get()
            table = user.xpath("//div[@id='user-rankings-all-time']/tbody//tr//td[2]/text()").getall()
            print(f'Profile {profile} joined KYM {joined}.')
            print(f''' 
            
            {table}


            ''')
            yield{
                'profile': profile,
                'role': role,
                'location': location,
                'joined_date': joined,
                'about': about,
            }