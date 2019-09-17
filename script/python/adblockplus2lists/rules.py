import base64
import os
import urllib.request

import requests


class Rules(object):
    __text: str

    def __init__(self):
        self.text = ""

    def add(self, url, is_base64=False):
        txt = self.__download_rules(url)
        if is_base64:
            txt = base64.b64decode(txt).decode("utf-8")
        self.text = self.text + txt + os.linesep
        return self

    def __download_rules(self, url: str) -> str:
        print("downloading rule [%s] ..." % url)
        all_text = ""
        response = requests.get(url, proxies=urllib.request.getproxies())
        if response.status_code == requests.codes.ok:
            all_text = response.text
        return all_text

    @property
    def text(self) -> str:
        return self.__text

    @text.setter
    def text(self, text: str) -> None:
        self.__text = text
