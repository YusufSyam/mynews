from bson import ObjectId
from .datetime_utils import *
from .db_class import *

def get_all_news():
    return News.objects()

def get_news_length():
    return len(News.objects())

def get_latest_news(page=1, limit=5):
    return News.objects().order_by('-uploaded_date').skip((page - 1) * limit).limit(limit)

def get_most_popular_news(news_per_page):
    return News.objects().order_by('-read_count').limit(news_per_page)

def get_news_by_id(news_id):
    return News.objects(pk=ObjectId(news_id)).first()

def get_news_by_writer(writer):
    return News.objects(writer=writer.pk)

def get_news_by_category(category):
    return News.objects(category=category.pk)

def get_all_categories():
    return list(Categories.objects())

def get_category_by_id(category_id):
    return Categories.objects(pk=ObjectId(category_id)).first()

def get_categories_by_news(news):
    return [Categories.objects(pk=ObjectId(i.category)).first() for i in news]

def get_category_by_category(category):
    return Categories.objects(category=category).first()

def get_all_writers():
    return Writer.objects()

def get_writer_by_id(writer_id):
    return Writer.objects(pk=ObjectId(writer_id)).first()

def get_writer_by_username(username):
    return Writer.objects(username= username).first()

def get_writer_by_news(news):
    return [Writer.objects(pk=ObjectId(i.writer)).first() for i in news]

def get_top_n_tags(n_limit):
    return list(News.objects().aggregate([
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": n_limit},
    ]))

def get_all_tags():
    return list(News.objects().aggregate([
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]))

def get_sort_by(type='category'):
    if(type=='category'):
        category = [i for i in News.objects().distinct('category')]
        selected_data = enumerate([News.objects(category=i) for i in category])
        category = [Categories.objects(pk=ObjectId(i)).first().category for i in category]
        sorted_by = category

    elif(type=='month_and_year'):
        distinct_date = [i for i in News.objects().distinct('uploaded_date')]
        selected_data_date = [News.objects(uploaded_date=i) for i in distinct_date]

        selected_data = []
        distinct_month_and_year = list(set([extract_month_and_year(i) for i in distinct_date]))
        for i in distinct_month_and_year:
            temp = []
            for j in selected_data_date:
                for k in j:
                    # return str((match_month_and_year(k.uploaded_date)))
                    if (match_month_and_year(i, k.uploaded_date)):
                        temp.append(k)

            selected_data.append(temp)

        selected_data = enumerate(selected_data)
        month_and_year = [get_convenience_month_and_year(i) for i in distinct_month_and_year]
        sorted_by = month_and_year
    else:
        tags = [i['_id'] for i in list(News.objects().aggregate([
            {"$unwind": "$tags"},
            {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]))]

        aggregation = [News.objects().aggregate([{"$match": {"tags": {"$elemMatch": {"$eq": f'{i}'}}}}]) for i in tags]
        selected_data= enumerate([[News.objects(pk=j['_id']).first() for j in i] for i in aggregation])
        sorted_by = tags
        # return str([[News(j) for j in i] for idx, i in selected_data])

    return selected_data, sorted_by

def get_news_with(type, sub_type):
    if(type=='category'):
        category= Categories.objects(category=sub_type).first()
        selected_data= [get_news_by_category(category)]
    else:
        selected_data = [News.objects(tags=sub_type)]

    sorted_by = [sub_type + ' ' + type]
    return enumerate(selected_data), sorted_by

