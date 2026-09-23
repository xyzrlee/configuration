#!/usr/bin/env python3

import base64
import getopt
import re
import sys
import urllib.request
from pathlib import Path


def download(url: str) -> bytes:
    """
    Download GFWList from the specified URL.
    """
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "gfwlist2squid/1.0",
        },
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def decode_gfwlist(data: bytes) -> str:
    """
    Decode Base64-encoded GFWList content.
    """
    # Remove whitespace from Base64 input.
    data = re.sub(rb"\s+", b"", data)

    # Add missing Base64 padding if necessary.
    data += b"=" * (-len(data) % 4)

    decoded = base64.b64decode(data)

    return decoded.decode(
        "utf-8",
        errors="replace",
    )


def normalize_domain(domain: str) -> str | None:
    """
    Normalize a domain for Squid dstdomain ACL.

    Example:

        google.com

    becomes:

        .google.com

    The leading dot makes Squid match the domain
    and its subdomains.
    """
    domain = domain.strip().lower().rstrip(".")

    if not domain:
        return None

    # Remove optional port.
    if ":" in domain and not domain.startswith("["):
        domain = domain.split(":", 1)[0]

    # Reject values which cannot safely be represented
    # as a Squid dstdomain rule.
    if (
        "/" in domain
        or "*" in domain
        or "^" in domain
        or "|" in domain
        or domain.startswith("[")
    ):
        return None

    return "." + domain.lstrip(".")


def extract_domain(rule: str) -> str | None:
    """
    Convert AutoProxy domain rules to Squid dstdomain rules.

    Examples:

        ||google.com
        ||google.com^
        ||google.com/path

    become:

        .google.com
    """
    if not rule.startswith("||"):
        return None

    value = rule[2:]

    # Remove AutoProxy separator and everything after it.
    value = value.split("^", 1)[0]

    # Remove URL path.
    value = value.split("/", 1)[0]

    return normalize_domain(value)


def autoproxy_to_regex(rule: str) -> str | None:
    """
    Best-effort conversion from AutoProxy/Adblock syntax
    to a regular expression suitable for Squid url_regex.
    """
    rule = rule.strip()

    if not rule:
        return None

    #
    # Native regular expression:
    #
    # /example.*test/
    #
    if (
        len(rule) >= 2
        and rule.startswith("/")
        and rule.endswith("/")
    ):
        return rule[1:-1]

    anchor_start = False
    anchor_end = False

    #
    # AutoProxy start anchor:
    #
    # |http://example.com
    #
    if rule.startswith("|"):
        anchor_start = True
        rule = rule[1:]

    #
    # AutoProxy end anchor:
    #
    # example.com|
    #
    if rule.endswith("|"):
        anchor_end = True
        rule = rule[:-1]

    #
    # Escape regular-expression metacharacters.
    #
    escaped = re.escape(rule)

    #
    # AutoProxy wildcard:
    #
    # *
    #
    # becomes:
    #
    # .*
    #
    escaped = escaped.replace(
        r"\*",
        ".*",
    )

    #
    # AutoProxy separator:
    #
    # ^
    #
    # Roughly means either end-of-string or a character
    # that is not an alphanumeric / _-.% character.
    #
    escaped = escaped.replace(
        r"\^",
        r"([^A-Za-z0-9_\-.%]|$)",
    )

    if anchor_start:
        escaped = "^" + escaped

    if anchor_end:
        escaped += "$"

    return escaped


def parse_rules(text: str):
    """
    Parse decoded GFWList content.

    Returns:

        proxy_domains
        proxy_regex
        direct_domains
        direct_regex
        unsupported
    """
    proxy_domains = set()
    proxy_regex = set()

    direct_domains = set()
    direct_regex = set()

    unsupported = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        #
        # Ignore comments and metadata.
        #
        if line.startswith("!"):
            continue

        direct = False

        #
        # AutoProxy exception:
        #
        # @@||example.com
        #
        if line.startswith("@@"):
            direct = True
            line = line[2:]

        #
        # Prefer dstdomain whenever possible.
        #
        domain = extract_domain(line)

        if domain:
            if direct:
                direct_domains.add(domain)
            else:
                proxy_domains.add(domain)

            continue

        #
        # Fall back to url_regex.
        #
        regex = autoproxy_to_regex(line)

        if regex:
            if direct:
                direct_regex.add(regex)
            else:
                proxy_regex.add(regex)
        else:
            unsupported.append(raw_line)

    return (
        proxy_domains,
        proxy_regex,
        direct_domains,
        direct_regex,
        unsupported,
    )


def write_lines(
    path: Path,
    values,
) -> None:
    """
    Write sorted ACL entries to a file.
    """
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        for value in sorted(values):
            file.write(value)
            file.write("\n")


def print_usage(program_name: str) -> None:
    """
    Print command-line usage.
    """
    print(
        f"""Usage:

  {program_name} \\
    --gfwlist-url=<URL> \\
    --proxy-domain-file=<PATH> \\
    --proxy-regex-file=<PATH> \\
    --direct-domain-file=<PATH> \\
    --direct-regex-file=<PATH> \\
    --unsupported-file=<PATH>

Required options:

  --gfwlist-url=<URL>
      GFWList download URL.

  --proxy-domain-file=<PATH>
      Output file for proxy dstdomain rules.

  --proxy-regex-file=<PATH>
      Output file for proxy url_regex rules.

  --direct-domain-file=<PATH>
      Output file for direct dstdomain rules.

  --direct-regex-file=<PATH>
      Output file for direct url_regex rules.

  --unsupported-file=<PATH>
      Output file for unsupported rules.

Other options:

  --help
      Show this help message.
"""
    )


def parse_arguments(argv):
    """
    Parse command-line arguments using getopt.

    All configuration options are required.
    """
    long_options = [
        "gfwlist-url=",
        "proxy-domain-file=",
        "proxy-regex-file=",
        "direct-domain-file=",
        "direct-regex-file=",
        "unsupported-file=",
        "help",
    ]

    try:
        options, arguments = getopt.getopt(
            argv,
            "",
            long_options,
        )
    except getopt.GetoptError as exc:
        print(
            f"Error: {exc}",
            file=sys.stderr,
        )

        print_usage(sys.argv[0])

        sys.exit(2)

    config = {}

    for option, value in options:
        if option == "--help":
            print_usage(sys.argv[0])
            sys.exit(0)

        elif option == "--gfwlist-url":
            config["gfwlist_url"] = value

        elif option == "--proxy-domain-file":
            config["proxy_domain_file"] = Path(value)

        elif option == "--proxy-regex-file":
            config["proxy_regex_file"] = Path(value)

        elif option == "--direct-domain-file":
            config["direct_domain_file"] = Path(value)

        elif option == "--direct-regex-file":
            config["direct_regex_file"] = Path(value)

        elif option == "--unsupported-file":
            config["unsupported_file"] = Path(value)

    #
    # Reject unexpected positional arguments.
    #
    if arguments:
        print(
            "Error: unexpected arguments: "
            + " ".join(arguments),
            file=sys.stderr,
        )

        print_usage(sys.argv[0])

        sys.exit(2)

    #
    # Check required options.
    #
    required_options = {
        "gfwlist_url": "--gfwlist-url",
        "proxy_domain_file": "--proxy-domain-file",
        "proxy_regex_file": "--proxy-regex-file",
        "direct_domain_file": "--direct-domain-file",
        "direct_regex_file": "--direct-regex-file",
        "unsupported_file": "--unsupported-file",
    }

    missing = [
        option_name
        for key, option_name in required_options.items()
        if key not in config
    ]

    if missing:
        print(
            "Error: missing required options: "
            + ", ".join(missing),
            file=sys.stderr,
        )

        print_usage(sys.argv[0])

        sys.exit(2)

    #
    # Reject empty values.
    #
    empty = [
        option_name
        for key, option_name in required_options.items()
        if not str(config[key]).strip()
    ]

    if empty:
        print(
            "Error: empty values are not allowed: "
            + ", ".join(empty),
            file=sys.stderr,
        )

        sys.exit(2)

    return config


def main() -> int:
    """
    Main entry point.
    """
    config = parse_arguments(
        sys.argv[1:]
    )

    try:
        #
        # Download GFWList.
        #
        print(
            "Downloading GFWList: "
            + config["gfwlist_url"],
            file=sys.stderr,
        )

        data = download(
            config["gfwlist_url"]
        )

        #
        # Decode Base64 content.
        #
        text = decode_gfwlist(
            data
        )

        #
        # Parse rules.
        #
        (
            proxy_domains,
            proxy_regex,
            direct_domains,
            direct_regex,
            unsupported,
        ) = parse_rules(text)

        #
        # Write Squid ACL files.
        #
        write_lines(
            config["proxy_domain_file"],
            proxy_domains,
        )

        write_lines(
            config["proxy_regex_file"],
            proxy_regex,
        )

        write_lines(
            config["direct_domain_file"],
            direct_domains,
        )

        write_lines(
            config["direct_regex_file"],
            direct_regex,
        )

        write_lines(
            config["unsupported_file"],
            unsupported,
        )

        #
        # Statistics.
        #
        print(
            f"Proxy domains : {len(proxy_domains)}"
        )

        print(
            f"Proxy regex   : {len(proxy_regex)}"
        )

        print(
            f"Direct domains: {len(direct_domains)}"
        )

        print(
            f"Direct regex  : {len(direct_regex)}"
        )

        print(
            f"Unsupported   : {len(unsupported)}"
        )

        return 0

    except Exception as exc:
        print(
            f"Error: {exc}",
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())
