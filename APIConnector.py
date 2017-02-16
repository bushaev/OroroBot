import requests


class APIConnector:

    def __init__(self, credentials):
        self.login, self.password = credentials

    def get(self, url, data=None):
        return requests.get(url, auth=(self.login, self.password),
                            headers={'User-Agent': 'runscope/0.1'})

    def post(self, url, data=None):
        return requests.post(url, auth=(self.login, self.password),
                             headers={'User-Agent': 'runscope/0.1'},
                             data=data)

    def put(self, url, data=None):
        return requests.put(url, auth=(self.login, self.password),
                            headers={'User-Agent': 'runscope/0.1'},
                            data=data)

    def try_request(self, req, url, handler, data=None):
        for _ in range(3):
            r = req(url, data)
            if r.status_code != 200:
                handler(r.status_code)
            else:
                return r
        handler(r.status_code, True)
        return r

    def try_get(self, url, handler, data=None):
        return self.try_request(self.get, url, handler, data)

    def try_post(self, url, handler, data=None):
        return self.try_request(self.post, url, handler, data)

    def try_put(self, url, handler, data=None):
        return self.try_request(self.put, url, handler, data)


class APIRequestSender:

    def __init__(self, credentials, handler):
        self.con = APIConnector(credentials)
        self.handler = handler

    def try_get_json(self, url):
        r = self.con.try_get(url, self.handler)
        if r.status_code is 200:
            return r.json()
        else:
            return None

    def show_list_json(self):
        return self.try_get_json("https://ororo.tv/api/v2/shows")

    def show_json(self, id):
        return self.try_get_json('https://ororo.tv/api/v2/shows/{0}'.format(
            id
        ))

    def episode_json(self, id):
        return self.try_get_json('https://ororo.tv/api/v2/episodes/{0}'.format(
            id
        ))
