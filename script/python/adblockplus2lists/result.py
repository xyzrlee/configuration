import ipaddress
import sys
from typing import MutableSet
from typing import Tuple

import tld
import validators
from sortedcontainers import SortedSet


def key_domain(dom: str) -> Tuple[str, str, str]:
    t = tld.parse_tld(dom, fail_silently=True, fix_protocol=True)
    return (t[1], t[0], t[2]) if t else (dom, "", "")


def key_ip(ip: str) -> int:
    return int(ipaddress.ip_network(ip, strict=False).network_address)


class Result(object):
    __domain: MutableSet[str] = SortedSet(key=key_domain)
    __domain_suffix: MutableSet[str] = SortedSet(key=key_domain)
    __ipv4_cidr: MutableSet[str] = SortedSet(key=key_ip)
    __ipv6_cidr: MutableSet[str] = SortedSet(key=key_ip)
    __url_regex: MutableSet[str] = SortedSet()

    def __init__(self):
        pass

    def add(self, to_list: MutableSet[str], text: str, remove: bool = False):
        if str:
            if remove:
                to_list.discard(text)
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
            if validators.ip_address.ipv4(ip, cidr=True):
                print("IP-CIDR,%s,no-resolve" % ip, file=out)
            else:
                print("IP-CIDR,%s/32,no-resolve" % ip, file=out)
        for ip in self.ipv6_cidr:
            if validators.ip_address.ipv6(ip, cidr=True):
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
            if not validators.ip_address.ipv4(ip, cidr=True):
                print("%s" % ip, file=out)
        for ip in self.ipv6_cidr:
            if not validators.ip_address.ipv6(ip, cidr=True):
                print("%s" % ip, file=out)
        x = SortedSet().union(self.domain).union(self.domain_suffix)
        for d in x:
            print(".%s" % d, file=out)

    def write_surge_domain_set(self, file=sys.stdout):
        out = file
        if not file: out = sys.stdout
        for dom in self.domain:
            print("%s" % dom, file=out)
        for dom in self.domain_suffix:
            print(".%s" % dom, file=out)

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
