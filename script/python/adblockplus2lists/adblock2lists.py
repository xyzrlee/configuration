import re
import urllib.parse

import abp.filters
import tld
import validators
from abp.filters.parser import Filter, Comment, Metadata, EmptyLine, FilterAction, SelectorType

from .result import Result
from .rules import Rules


class AdblockPlus2Lists(object):
    __rules: Rules
    __ignore_path: bool

    def __init__(self, rules: Rules, ignore_path: bool = False):
        self.rules = rules
        self.__ignore_path = ignore_path
        tld.utils.update_tld_names()

    def convert(self) -> Result:
        print("conversion begins")
        result = Result()
        lines = self.rules.text.splitlines()
        total_lines = len(lines)
        print("[%r] lines in total" % total_lines)
        perc, l = 0, 0
        for rule_str in lines:
            self.__do_convert(result, rule_str)
            l = l + 1
            p = int(l / total_lines * 100)
            if (p - perc >= 10):
                print("%r%% converted" % p)
                perc = int(p / 10) * 10
        return result

    def __do_convert(self, result: Result, rule: str, is_allow: bool = False) -> None:
        abp_result = abp.filters.parse_line(rule)
        if isinstance(abp_result, EmptyLine):
            return
        elif isinstance(abp_result, Comment):
            return
        elif isinstance(abp_result, Metadata):
            return
        elif isinstance(abp_result, Filter):
            if abp_result.action == FilterAction.HIDE:
                return
            if abp_result.action == FilterAction.ALLOW:
                self.__do_convert(result, abp_result.selector["value"], True)
                return
            if len(abp_result.options) > 0:
                return
            if abp_result.selector:
                # print(abp_result)
                if abp_result.selector["type"] == SelectorType.URL_PATTERN:
                    self.__do_convert_url_pattern(result, abp_result.selector["value"], is_allow)
                    return
                elif abp_result.selector["type"] == SelectorType.URL_REGEXP:
                    self.__do_convert_url_regex(result, abp_result.selector["value"], is_allow)
                    return
                else:
                    self.print_ignored(abp_result)
                    return
        else:
            self.print_ignored(abp_result)

    def __do_convert_url_pattern(self, result: Result, s: str, is_allow: bool) -> None:
        t = s
        is_domain_suffix = True
        if t.startswith("||"):
            t = t[2:]
            is_domain_suffix = True
        if t.startswith("|"):
            t = t[1:]
            is_domain_suffix = False
        if t.startswith("."):
            t = t[1:]
            is_domain_suffix = True
        t = re.sub(r"^https?://", "", t)
        t = t.lstrip("*.").rstrip("^/*")
        ur = urllib.parse.urlparse("http://" + t)
        if ur.path and not self.ignore_path:
            return
        t = ur.netloc
        t = re.sub(r":\d{2,5}$", "", t)
        if validators.ipv4(t) or validators.ipv4_cidr(t):
            result.add(result.ipv4_cidr, t, remove=is_allow)
        elif validators.ipv6(t) or validators.ipv6_cidr(t):
            result.add(result.ipv6_cidr, t, remove=is_allow)
        else:
            if validators.domain(t) and tld.get_fld(t, fail_silently=True, fix_protocol=True):
                if is_domain_suffix:
                    result.add(result.domain_suffix, t, remove=is_allow)
                else:
                    result.add(result.domain, t, remove=is_allow)

    def __do_convert_url_regex(self, result: Result, s: str, is_allow: bool) -> None:
        result.add(result.url_regex, s, remove=is_allow)

    def print_ignored(self, abp_result):
        print("ignored:", abp_result)

    @property
    def rules(self) -> Rules:
        return self.__rules

    @rules.setter
    def rules(self, rules: Rules):
        self.__rules = rules

    @property
    def ignore_path(self) -> bool:
        return self.__ignore_path

    @ignore_path.setter
    def ignore_path(self, ignore_path: bool):
        self.__ignore_path = ignore_path
