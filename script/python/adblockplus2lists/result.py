import sys
from typing import MutableSet

import validators
from sortedcontainers import SortedSet


class Result(object):
    __domain: MutableSet[str] = SortedSet()
    __domain_suffix: MutableSet[str] = SortedSet()
    __ipv4_cidr: MutableSet[str] = SortedSet()
    __ipv6_cidr: MutableSet[str] = SortedSet()
    __url_regex: MutableSet[str] = SortedSet()

    def __init__(self):
        pass

    def add(self, to_list: MutableSet[str], text: str, remove: bool = False):
        if str:
            if remove:
                try:
                    to_list.remove(text)
                except KeyError:
                    pass
            else:
                to_list.add(text)
        return self

    def print_statistics(self) -> None:
        print("domain           %r" % len(self.domain))
        print("domain_suffix    %r" % len(self.domain_suffix))
        print("ipv4_cidr        %r" % len(self.ipv4_cidr))
        print("ipv6_cidr        %r" % len(self.ipv6_cidr))
        print("url_regex        %r" % len(self.url_regex))

    def write_surge(self, file=sys.stdout):
        out = file
        if not file: out = sys.stdout
        for dom in self.domain:
            print("DOMAIN,%s" % dom, file=out)
        for dom in self.domain_suffix:
            print("DOMAIN-SUFFIX,%s" % dom, file=out)
        for ip in self.ipv4_cidr:
            if validators.ipv4_cidr(ip):
                print("IP-CIDR,%s,no-resolve" % ip, file=out)
            else:
                print("IP-CIDR,%s/32,no-resolve" % ip, file=out)
        for ip in self.ipv6_cidr:
            if validators.ipv6_cidr(ip):
                print("IP-CIDR6,%s,no-resolve" % ip, file=out)
            else:
                print("IP-CIDR6,%s/128,no-resolve" % ip, file=out)
        for url_regex in self.url_regex:
            print("url-regex: %s" % url_regex)

    def write_privoxy(self, forward: str, proxy: str, file=sys.stdout):
        out = file
        if not file: out = sys.stdout
        print("{+forward-override{forward-%s %s .}}" % (forward, proxy), file=out)
        for ip in self.ipv4_cidr:
            if not validators.ipv4_cidr(ip):
                print("%s" % ip, file=out)
        for ip in self.ipv6_cidr:
            if not validators.ipv6_cidr(ip):
                print("%s" % ip, file=out)
        x = SortedSet().union(self.domain).union(self.domain_suffix)
        for d in x:
            print(".%s" % d, file=out)

    @property
    def domain(self) -> MutableSet:
        return self.__domain

    @domain.setter
    def domain(self, domain: MutableSet) -> None:
        self.__domain = domain

    @property
    def domain_suffix(self) -> MutableSet:
        return self.__domain_suffix

    @domain_suffix.setter
    def domain_suffix(self, domain_suffix: MutableSet) -> None:
        self.__domain_suffix = domain_suffix

    @property
    def ipv4_cidr(self) -> MutableSet:
        return self.__ipv4_cidr

    @ipv4_cidr.setter
    def ipv4_cidr(self, ipv4_cidr: MutableSet) -> None:
        self.__ipv4_cidr = ipv4_cidr

    @property
    def ipv6_cidr(self) -> MutableSet:
        return self.__ipv6_cidr

    @ipv6_cidr.setter
    def ipv6_cidr(self, ipv6_cidr: MutableSet) -> None:
        self.__ipv6_cidr = ipv6_cidr

    @property
    def url_regex(self) -> MutableSet:
        return self.__url_regex

    @url_regex.setter
    def url_regex(self, url_regex: MutableSet) -> None:
        self.__url_regex = url_regex
