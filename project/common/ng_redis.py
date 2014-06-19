#encoding=UTF8
#code by T
#2013-8-19

import random
from redis import Redis,ConnectionPool
#from conf.settings import settings

class NGRedis(object):
    def __init__(self, settings):
        #print settings
        #exit()
        self.master = settings['redis_master']
        self.conn_master = self.conn_redis(**self.master)
        if 'redis_slave' in settings:
            self.slaves = settings['redis_slave']
            self.conn_slave_redis_group = self.init_slaves(self.slaves )
        
    def init_slaves(self, slaves):
        conn_slave_redis_group = []
        for slave in slaves:
                r = self.conn_redis(**slave)
                if not r:continue
                conn_slave_redis_group.append(r)      
        return conn_slave_redis_group
    
    def get_redis(self, source=False):
        '''
        提供一个可使用的redis对象。
        参数 source : True为master / Flase为slave随即对象
        '''
        if source:
            r = self.conn_master
            #print dir(r)
            if r.ping:
                return  r
            else:
                return None
        else:
            r = self.random_slave_redis()
            while not r.ping:
                r = self.random_slave_redis()
            return r
        return None
    
    def conn_redis(self, **redis_conf):
        r = None
        try:
            #pool = ConnectionPool(host=redis_conf['host'], port=redis_conf['port'] , password=redis_conf['pwd'])
            pool = ConnectionPool(**redis_conf)
            r = Redis(connection_pool=pool)
        except Exception,e:
            print 'conn_redis error,msg:' + str(e)
        return r
    
    def random_slave_redis(self):     
        return random.choice(self.conn_slave_redis_group)
    
if __name__ == '__main__':
    #from comm.ng_redis import NGRedis
    ng_redis = NGRedis()
    master_redis = ng_redis.get_redis(source=True)
    slave_redis = ng_redis.get_redis()

    key = 'xxoo123123'
    master_redis.lpush(key , '妹子1号')
    master_redis.lpush(key , '妹子2号')
    master_redis.lpush(key , '妹子3号')
    master_redis.lpush(key , '妹子4号')
    master_redis.lpush(key , '妹子5号')
    master_redis.lpush(key , '妹子6号')
    master_redis.lpush(key , '妹子7号')
    print master_redis.brpop(key)[1]  #==> 妹子1号
    print master_redis.brpop(key)[1]  #==> 妹子2号
    print slave_redis.lrange(key, 0, -1)   #剩下的所有
    master_redis.delete(key)
        
        

