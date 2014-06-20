# -*- coding: utf-8 -*-
# Created by pengchangliang on 14-3-22.

import math
import pyes
from conf.settings import settings


class AppSearch(object):
    def __init__(self):
        self.index = settings['elasticsearch']['index']
        self.es = pyes.ES('%s:%s' % (settings['elasticsearch']['host'], settings['elasticsearch']['port']))

    def create_index(self):
        try:
            #新建一个索引
            self.es.indices.create_index(self.index)
            #定义索引存储结构
            mapping = {
                u'trackName': {'boost': 2.0,
                               'index': 'analyzed',
                               'store': 'yes',
                               'type': u'string',
                               "term_vector": "with_positions_offsets"},

                u'supportIphone': {'boost': 1.0,
                                   'index': 'not_analyzed',
                                   'store': 'yes',
                                   'type': u'integer'},
                u'supportIpad': {'boost': 1.0,
                                 'index': 'not_analyzed',
                                 'store': 'yes',
                                 'type': u'integer'},
                u'sign': {'boost': 1.0,
                                 'index': 'not_analyzed',
                                 'store': 'yes',
                                 'type': u'integer'},
                u'bundleId': {'boost': 1.0,
                              'index': 'not_analyzed',
                              'store': 'yes',
                              'type': u'string'},
                u'ID': {'boost': 1.0,
                              'index': 'not_analyzed',
                              'store': 'yes',
                              'type': u'string'},
                u'ipaVersionJb': {'boost': 1.0,
                          'index': 'not_analyzed',
                          'store': 'yes',
                          'type': u'string'},
                u'ipaVersionSigned': {'boost': 1.0,
                          'index': 'not_analyzed',
                          'store': 'yes',
                          'type': u'string'},
                u'icon': {'boost': 1.0,
                          'index': 'not_analyzed',
                          'store': 'yes',
                          'type': u'string'},
                u'size': {'boost': 1.0,
                          'index': 'not_analyzed',
                          'store': 'yes',
                          'type': u'string'},
                u'averageUserRating': {'boost': 1.0,
                            'index': 'not_analyzed',
                            'store': 'yes',
                            'type': u'float'}
            }

            self.es.indices.put_mapping("apps", {'properties': mapping}, [self.index])
        except Exception, ex:
            print ex

    def add_index(self, ID, track_name, support_iphone, support_ipad, bundle_id, icon, rating, size, sign, ipa_version_jb, ipa_version_signed):
        self.es.index(
            {
              'ID': ID, 
              'trackName': track_name, 
              'supportIphone': support_iphone, 
              'supportIpad': support_ipad,
              'bundleId': bundle_id,
              'icon': icon, 
              'averageUserRating': rating, 
              'size': size, 
              'sign': sign,
              'ipaVersionJb': ipa_version_jb, 
              'ipaVersionSigned': ipa_version_signed
             },
            self.index, "apps", ID)

    def query(self, words, device, sign=0, page=1, page_size=12):
        """
        query
        """
        start = (page - 1) * page_size
        
        should = [pyes.TextQuery('trackName', words)]
        must = []
        if sign == 1:
          must.append(pyes.TermQuery('sign', 1))
        must_not = []
        if device == 'iphone':
            must_not.append(pyes.TermQuery('supportIphone', 0))

        results = self.es.search(
            pyes.Search(pyes.BoolQuery(must=must, must_not=must_not, should=should),
                        fields=['trackName', 'icon', 'ID', 'bundleId', 'averageUserRating',  
                        'size', 'ipaVersionJb', 'ipaVersionSigned', 'supportIphone', 'supportIpad'],
                        start=start,
                        size=page_size
            ))

        count = results.count()
        total_page = int(math.ceil(count / float(page_size)))
        prev_page = (page - 1) if page - 1 > 0 else 1
        next_page = (page + 1) if page + 1 < total_page else total_page
        items = []
        for item in results:
          if sign == 1:
            item['ipaVersion'] = item['ipaVersionSigned']
          else:
            item['ipaVersion'] = item['ipaVersionJb']
          del item['ipaVersionJb']
          del item['ipaVersionSigned']
          items.append(item)
        return {'results': items,
                'pageInfo': {'count': count, 'page': page, 'totalPage': total_page, 'prevPage': prev_page,
                             'nextPage': next_page}}

    def refresh(self):
        self.es.indices.refresh([self.index])

    def delete_index(self):
        self.es.indices.delete_index(self.index)
