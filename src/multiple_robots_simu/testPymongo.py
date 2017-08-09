>>> from pymongo import MongoClient
>>> client = MongoClient()
>>> db = client.test_database
>>> collection = db.test_collection
>>> import datetime
>>> post = {"author": "Mike",
... 
... "text": "My first blog post!",
... 
... "tags"
... 
... : ["mongodb", "python", "pymongo"],
... 
... "date": datetime.datetime.utcnow()}
>>> posts = db.posts
>>> post_id = collection.insert(post)
>>> post_id
ObjectId('59771ace0a38b50fc3d0af7c')
>>> import pprint
>>> pprint.pprint(posts.find())
<pymongo.cursor.Cursor object at 0x7fd6a6f16ed0>
>>> pprint.pprint(posts.find_one())
None
>>> pprint.pprint(collection.find_one())
{u'_id': ObjectId('59771ace0a38b50fc3d0af7c'),
 u'author': u'Mike',
 u'date': datetime.datetime(2017, 7, 25, 10, 10, 18, 32000),
 u'tags': [u'mongodb', u'python', u'pymongo'],
 u'text': u'My first blog post!'}
>>> pprint.pprint(collection.find())
<pymongo.cursor.Cursor object at 0x7fd6a6f16f10>

>>> new_posts = [{"author": "Mike",
... 
...  "text": "Another post!",
... 
... "tags": ["bulk", "insert"],
... 
... "date": datetime.datetime(2009, 11, 12, 11, 14)},
... 
... {"author": "Eliot",
... 
... "title": "MongoDB is fun",
... 
... "text": "and pretty easy too!",
... 
... "date": datetime.datetime(2009, 11, 10, 10, 45)}]
>>> result = posts.insert(new_posts)
>>> result
[ObjectId('59771da80a38b50fc3d0af7d'), ObjectId('59771da80a38b50fc3d0af7e')]

>>> for post in posts.find():
...     pprint.pprint(post)
... 
{u'_id': ObjectId('59771da80a38b50fc3d0af7d'),
 u'author': u'Mike',
 u'date': datetime.datetime(2009, 11, 12, 11, 14),
 u'tags': [u'bulk', u'insert'],
 u'text': u'Another post!'}
{u'_id': ObjectId('59771da80a38b50fc3d0af7e'),
 u'author': u'Eliot',
 u'date': datetime.datetime(2009, 11, 10, 10, 45),
 u'text': u'and pretty easy too!',
 u'title': u'MongoDB is fun'}
>>> 
