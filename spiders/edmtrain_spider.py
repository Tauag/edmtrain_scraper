from scrapy import Spider
from exceptions import DatabaseDuplicateException
import requests
import random
import time
import re


class EDMTrainSpider(Spider):
    name = 'generic edmtrain spider'
    start_urls = []
    allow_redirect = True
    db_conn = None

    def __init__(self, *args, **kwargs):
        if 'disable_redirect' in kwargs and kwargs['disable_redirect']:
            self.allow_redirect = False

        if 'db_conn' in kwargs and kwargs['db_conn'] is not None:
            # Requires the connection's autocommit to be set to True
            self.db_conn = kwargs['db_conn']
            self.db_conn.autocommit = True

        if 'callback_hook' in kwargs:
            self.callback_hook = kwargs['callback_hook']
        else:
            self.callback_hook = lambda item: item

        super(EDMTrainSpider, self).__init__(*args, **kwargs)

    def get_final_redirect(self, link):
        if link is None:
            return "No info"
        if not self.allow_redirect:
            return link, False

        # Wait randomly between 5 - 10 seconds to avoid being throttled
        wait_time = random.randrange(5, 10)
        time.sleep(wait_time)

        try:
            response = requests.get(link)
            return response.url, True
        except requests.exceptions.RequestException:
            return link, False

    def generate_extracts(self, response, parent, option='css'):
        option_mapping = {
            'css': response.css,
            'xpath': response.xpath
        }

        try:
            for event in option_mapping[option](parent):
                event_link = event.css('td.eventLink>a::attr(href)').extract_first()
                (redirected_link, check_redirect) = self.get_final_redirect(event_link)
                location = event.css('div.eventLocation>span[itemprop="location"]::text').extract_first()
                age = event.css('span.ageLabel::text').extract_first()

                extract = {
                    'title': event.xpath('@titlestr').extract_first(),
                    'event_id': event.xpath('@eventid').extract_first(),
                    'start_date': event.xpath('@sorteddate').extract_first(),
                    'venue': event.xpath('@venue').extract_first(),
                    'location': "No Info" if location is None else re.sub(r'( - )(?=[A-z0-9 ]+)', '', location),
                    'age_limit': age if age is not None else "No Info",
                    'link': redirected_link,
                    'redirect_success': check_redirect
                }

                yield extract
        except Exception as e:
            print(e)

    def new_cursor(self):
        if self.db_conn is not None:
            return self.db_conn.cursor(buffered=True)
        return None

    def log_into_database(self, extract):
        cursor = self.new_cursor()

        # Check if eventid is already in database
        query = f'SELECT title FROM events WHERE event_id = {extract["event_id"]}'
        if cursor.execute(query) is not None:
            raise DatabaseDuplicateException(f'Event {extract["title"]} with id: {extract["event_id"]} '
                                             f'is already saved into database')
        cursor.close()

        # Log new event into database
        query = f'INSERT INTO events (title, event_id, start_date, venue, location, age_limit, link, ' \
            f'redirect_success) VALUES ("{extract["title"]}", "{extract["event_id"]}", "{extract["start_date"]}",' \
            f' "{extract["venue"]}", "{extract["location"]}", "{extract["age_limit"]}", "{extract["link"]}", ' \
            f'"{"YES" if extract["redirect_success"] else "NO"}")'

        cursor = self.new_cursor()
        cursor.execute(query)
        cursor.close()
        
    def parse(self, response):
        pass
