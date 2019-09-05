import os
import typing

import requests
import validators


class Adblock2Surge(object):
    __rules: typing.List[str] = []

    def __init__(self, rules: typing.List[str]):
        self.rules = rules

    def convert(self, output_file_path: str) -> None:
        rule_text = self.__download_rules()
        filter_domain, filter_ipv4, filter_ipv6 = self.__convert_to_set(rule_text)
        self.__write_to_file(output_file_path, filter_domain, filter_ipv4, filter_ipv6)

    def __convert_to_set(self, rule_text: str) -> (typing.Set[str], typing.Set[str], typing.Set[str]):
        filter_domain: typing.Set[str] = set()
        filter_ipv4: typing.Set[str] = set()
        filter_ipv6: typing.Set[str] = set()
        for rule_str in rule_text.splitlines():
            if rule_str == "": continue
            if rule_str.startswith("!"): continue
            if "##" in rule_str: continue
            if "#@#" in rule_str: continue
            if "$" in rule_str: continue
            print("rule_str:%r" % rule_str)
            is_remove_rule = False
            if rule_str.startswith("@@"):
                rule_str = rule_str[2:]
                is_remove_rule = True
            if rule_str.startswith("||"):
                rule_str = rule_str[2:]
            rule_str = self.__remove_redundant(rule_str)
            self.__set_operation(filter_domain, self.__get_domain(rule_str), is_remove_rule)
            self.__set_operation(filter_ipv4, self.__get_ipv4(rule_str), is_remove_rule)
            self.__set_operation(filter_ipv6, self.__get_ipv6(rule_str), is_remove_rule)
        return (filter_domain, filter_ipv4, filter_ipv6)

    def __write_to_file(self, output_file_path: str, filter_domain: typing.Set[str], filter_ipv4: typing.Set[str],
                        filter_ipv6: typing.Set[str]) -> None:
        pass

    def __set_operation(self, s: typing.Set[str], rule_str: str, is_remove_rule: bool) -> None:
        if not rule_str: return
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

    def __remove_redundant(self, rule_str: str) -> str:
        result = rule_str.rstrip("^/")
        return result

    def __download_rules(self) -> str:
        all_text = ""
        for rule in self.rules:
            response = requests.get(rule)
            all_text = all_text + response.text + os.linesep
        return all_text

    @property
    def rules(self) -> typing.List[str]:
        return self.__rules

    @rules.setter
    def rules(self, rules: typing.List[str]):
        self.__rules = rules
