import requests  # version 2.28.1
from datetime import datetime


class MyRequest:
    def __init__(self, URL, payload):
        self.payload = payload
        self.URL = URL  # api endpoint
        self.response = None

    def send_request(self):

        try:
            # sending post request
            self.response = requests.post(url=self.URL, data=self.payload)
            self.response.raise_for_status()

        except requests.exceptions.InvalidURL:
            return 0
        except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema):
            return 1
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            return 2

    def get_result(self, counter):
        cnt = f'===={str(counter)}===='
        status_code = f'.status code: {self.response.status_code}'

        response = f'.response:    {self.response.text}'
        now = datetime.now()
        dt_string = now.strftime("%a, %d %b %Y %H:%M:%S")
        date = '.date:        {}'.format(dt_string)

        result = '\n'.join([cnt, status_code, response, date])

        return result