from spiders.edmtrain_spider import EDMTrainSpider
from exceptions import DatabaseDuplicateException
from scrapy import Request


class AllFestivalsSpider(EDMTrainSpider):
    name = "edmtrain all fests"
    url = 'https://edmtrain.com/get-festivals'

    def start_requests(self):
        return [Request(self.url, dont_filter=True)]

    def parse(self, response):
        generator = self.generate_extracts(response, '//div[@class="festivalEventContainer"]', option="xpath")
        if generator is None:
            # Log unable to generate
            return

        try:
            item = generator.__next__()

            while item is not None:
                try:
                    self.log_into_database(item)
                except DatabaseDuplicateException as e:
                    # Should log this exception
                    print(e)

                self.callback_hook(item)
                item = generator.__next__()
        except StopIteration:
            # End of generator
            return
