from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor, defer
from spiders.all_fests_spider import AllFestivalsSpider
from spiders.location_spider import AllLocationSpider, RecentLocationSpider
import mysql.connector
import time
from sys import exit

# Set up db connection
try:
    db_conn = mysql.connector.connect(host="127.0.0.1", user="root", password="password", database="database")
    db_conn.autocommit = True
except Exception as e:
    exit(e)

runner = CrawlerRunner({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})


@defer.inlineCallbacks
def crawl():
    # Put the spiders in this function

    # yield runner.crawl(AllFestivalsSpider, db_conn=db_conn, disable_redirect=True,
    #                    callback_hook=lambda item: print(item))

    # yield runner.crawl(AllLocationSpider, locations=['new york'], disable_redirect=True, db_conn=db_conn,
    #                    callback_hook=lambda item: print(item))

    yield runner.crawl(RecentLocationSpider, db_conn=db_conn, locations=['new york'], disable_redirect=False,
                       max_depth=1, callback_hook=lambda item: print(item))
    reactor.stop()


start = time.perf_counter()
crawl()
reactor.run()
end = time.perf_counter()
print(f'Crawler(s) took {end - start} seconds to complete')
# db_conn.close()
