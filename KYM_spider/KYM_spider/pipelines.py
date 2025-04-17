# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import re

# Custom image pipeline that names images image_name
class ImgIDPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None):
        # Building the name from the request URL, which contains img ID.
        # Image ID is after "newsfeed" in the URL
        image_name = request.url.split('newsfeed')[-1]
        # Clean URL string
        image_name = re.sub('/', '', image_name)
        # Get the file type (if it contains one)
        filetype = image_name.split('.')[-1]
        # If the image url doesn't have an extension:
        if filetype == image_name:
            # The first 9 characters are the img ID
            image_name = image_name[:9]
            image_name = 'img_'+image_name+'.jpg'
        # If the image has an extension:
        else:
            # The first 9 characters are the img ID
            image_name = image_name[:9]
            image_name = 'img_'+image_name+'.'+ filetype    

        return image_name

# Weird URL image examples that need to be named correctly for image_name
#   "https://i.kym-cdn.com/photos/images/newsfeed/001/160/795/747"
