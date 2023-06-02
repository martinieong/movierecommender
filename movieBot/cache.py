import redis
import numpy as np
import json


class RedisCache:
    def __init__(self,name):
        self.redis = redis.Redis(host=name,port=6379,db=0,decode_responses=True)
    
    def set_python_dict(self,key,value):
        self.redis.set(key,json.dumps(value))
    
    def get_python_dict(self,key):
        return json.loads(self.redis.get(key))
    
    def delete_python_dict(self,key):
        self.redis.delete(key)

    def get_all_keys(self):
        return list(self.redis.keys("*"))


