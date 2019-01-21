from spiders.edmtrain_spider import EDMTrainSpider
from exceptions import DatabaseDuplicateException
import requests


class AllLocationSpider(EDMTrainSpider):
    name = "edmtrain specific location"
    start_urls = []

    def __init__(self, *args, **kwargs):
        if 'locations' in kwargs:
            self.set_locations(kwargs['locations'])

        super(AllLocationSpider, self).__init__(*args, **kwargs)

    def set_locations(self, locations):
        to_search = []
        for location in locations:
            response = requests.post('https://edmtrain.com/search-location', data={'search': location})
            to_search.append(f'https://edmtrain.com/get-events?locationIdArray%5B%5D={response.json()["data"]["id"]}')

        self.start_urls = to_search

    def parse(self, response):
        generator = self.generate_extracts(response, '//div[@class="eventContainer"]', option="xpath")

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


class RecentLocationSpider(AllLocationSpider):
    name = 'edmtrain new additions location specific'
    last_eventid = ''
    max_depth = 10

    def __init__(self, *args, **kwargs):
        if 'last_eventid' in kwargs:
            self.last_event = kwargs['last_eventid']

        if 'max_depth' in kwargs:
            self.max_depth = kwargs['max_depth']

        super(RecentLocationSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        counter = 0
        extract = self.generate_extracts(response, f'//div[@sequence="{counter}"]', 'xpath')

        try:
            # If there is no sequence number 0, assume something is wrong
            extract_item = extract.__next__()
        except Exception:
            # Log an error here
            return

        while extract_item['event_id'] != self.last_eventid and counter < self.max_depth:
            try:
                self.log_into_database(extract_item)
                self.callback_hook(extract_item)
                extract_item = extract.__next__()
            except DatabaseDuplicateException as e:
                # Should log this exception
                print(e)
            except Exception:
                counter += 1
                extract = self.generate_extracts(response, f'//div[@sequence="{counter}"]', 'xpath')
                extract_item = extract.__next__()
