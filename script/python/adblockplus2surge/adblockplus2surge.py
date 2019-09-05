import os
import typing

import requests
import validators
import sys
import contextlib
import re
import sortedcontainers
import http


class AdblockPlus2Surge(object):
    __rules: typing.AbstractSet[str] = set()

    def __init__(self, rules: typing.Union[typing.AbstractSet[str], typing.List[str]]):
        if isinstance(rules, list):
            self.rules = set(rules)
        if isinstance(rules, set):
            self.rules = rules

    def convert(self, output_file_path: str) -> None:
        rule_text = self.__download_rules()
        filter_domain, filter_domain_suffix, filter_ipv4, filter_ipv6 = self.__convert_to_set(rule_text)
        print("filter_domain=%r" % len(filter_domain))
        print("filter_domain_suffix=%r" % len(filter_domain_suffix))
        print("filter_ipv4=%r" % len(filter_ipv4))
        print("filter_ipv6=%r" % len(filter_ipv6))
        self.__write_to_file(
            output_file_path,
            filter_domain,
            filter_domain_suffix,
            filter_ipv4,
            filter_ipv6
        )

    def __convert_to_set(self, rule_text: str) -> (
            typing.AbstractSet[str], typing.AbstractSet[str], typing.AbstractSet[str], typing.AbstractSet[str]
    ):
        filter_domain: typing.MutableSet[str] = sortedcontainers.SortedSet()
        filter_domain_suffix: typing.MutableSet[str] = sortedcontainers.SortedSet()
        filter_ipv4: typing.MutableSet[str] = sortedcontainers.SortedSet()
        filter_ipv6: typing.MutableSet[str] = sortedcontainers.SortedSet()
        for rule_str in rule_text.splitlines():
            if rule_str == "":
                continue
            if rule_str.startswith("!"):
                continue
            if "##" in rule_str:
                continue
            if "#@#" in rule_str:
                continue
            if "$" in rule_str:
                continue
            is_remove_rule = False
            is_domain_suffix = False
            if rule_str.startswith("@@"):
                rule_str = rule_str[2:]
                is_remove_rule = True
            if rule_str.startswith("||"):
                rule_str = rule_str[2:]
                is_domain_suffix = True
            if rule_str.startswith("|"):
                rule_str = rule_str[1:]
            rule_str = self.__remove_redundant(rule_str)
            if is_domain_suffix:
                self.__set_operation(filter_domain_suffix, self.__get_domain(rule_str), is_remove_rule)
            else:
                self.__set_operation(filter_domain, self.__get_domain(rule_str), is_remove_rule)
            self.__set_operation(filter_ipv4, self.__get_ipv4(rule_str), is_remove_rule)
            self.__set_operation(filter_ipv6, self.__get_ipv6(rule_str), is_remove_rule)
        for ip in filter_ipv4 | filter_ipv6:
            try:
                filter_domain.remove(ip)
            except KeyError:
                pass
            try:
                filter_domain_suffix.remove(ip)
            except KeyError:
                pass
        return (
            filter_domain,
            filter_domain_suffix,
            filter_ipv4,
            filter_ipv6
        )

    def __write_to_file(self,
                        output_file_path: str,
                        filter_domain: typing.AbstractSet[str],
                        filter_domain_suffix: typing.AbstractSet[str],
                        filter_ipv4: typing.AbstractSet[str],
                        filter_ipv6: typing.AbstractSet[str]
                        ) -> None:
        with self.__open(output_file_path, "w") as f:
            for domain in filter_domain:
                print("DOMAIN,%s" % domain, file=f)
            for domain_suffix in filter_domain_suffix:
                print("DOMAIN-SUFFIX,%s" % domain_suffix, file=f)
            for ipv4 in filter_ipv4:
                print("IP-CIDR,%s,no-resolve" % ipv4, file=f)
            for ipv6 in filter_ipv6:
                print("IP-CIDR6,%s,no-resolve" % ipv6, file=f)

    @contextlib.contextmanager
    def __open(self, file_path, mode):
        if file_path:
            f = open(file_path, mode)
        else:
            f = sys.stdout
        try:
            yield f
        finally:
            if f is not sys.stdout:
                f.close()

    @staticmethod
    def __set_operation(s: typing.MutableSet[str], rule_str: str, is_remove_rule: bool) -> None:
        if not rule_str:
            return
        if is_remove_rule:
            try:
                s.remove(rule_str)
            except KeyError:
                pass
        else:
            s.add(rule_str)

    def __get_domain(self, rule_str: str) -> typing.Optional[str]:
        if validators.domain(self.__remove_redundant(rule_str)):
            return rule_str
        return None

    def __get_ipv4(self, rule_str: str) -> typing.Optional[str]:
        if validators.ipv4(self.__remove_redundant(rule_str)):
            return rule_str
        return None

    def __get_ipv6(self, rule_str: str) -> typing.Optional[str]:
        if validators.ipv6(self.__remove_redundant(rule_str)):
            return rule_str
        return None

    @staticmethod
    def __remove_redundant(rule_str: str) -> str:
        result = rule_str.rstrip("^/*")
        result = result.lstrip(".*")
        result = re.sub(r'^\|?https?://', '', result)
        result = re.sub(r':\d{2,5}$', '', result)
        return result

    def __download_rules(self) -> str:
        all_text = ""
        for rule in self.rules:
            response = requests.get(rule)
            if response.status_code == requests.codes.ok:
                all_text = all_text + response.text + os.linesep

        return all_text

    @property
    def rules(self) -> typing.AbstractSet[str]:
        return self.__rules

    @rules.setter
    def rules(self, rules: typing.AbstractSet[str]):
        self.__rules = rules
