import os
from .db_class import *

def get_news_image_path_list():
    img_path_list= [i['img_path'] for i in list(News.objects().aggregate([{"$project" : {"_id":0, "img_path":1}}]))]
    return img_path_list

def handle_duplicate_img_filename(filename):
    filename = filename.split('.')
    filename[-2] = filename[-2] + '(2)'
    filename = '.'.join(filename)

    return filename

def delete_image_of(path, folder_location):
    img_deleted_news = os.path.join(os.getcwd(), ('static/'+folder_location), path)
    if os.path.exists(img_deleted_news):
        os.remove(img_deleted_news)