from flask_mongoengine import MongoEngine

db = MongoEngine()
def set_db(app):
    global db
    db.init_app(app)
    return db

class Categories(db.Document):
    category= db.StringField()

class Writer(db.Document):
    username=  db.StringField()
    password= db.StringField()
    authority= db.StringField()
    profile_pict_path= db.StringField()

class News(db.Document):
    title= db.StringField(required=True)
    category= db.ObjectIdField(required=True)
    uploaded_date= db.DateField(required=True)
    tags= db.ListField(required=True)
    writer= db.ObjectIdField(required=True)
    img_path= db.StringField()
    read_count= db.IntField()
    content= db.StringField(required=True)