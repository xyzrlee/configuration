import getopt
import sys

from adblockplus2lists import AdblockPlus2Lists, Result, Rules


def main(argv) -> None:
    output_file = None
    rules = Rules()
    opts, args = getopt.getopt(argv, "", [
        "output-file=", "abp-rule=", "abp-rule-base64="
    ])
    for opt, arg in opts:
        if opt == "--output-file":
            output_file = arg
        elif opt == "--abp-rule":
            rules.add(arg)
        elif opt == "--abp-rule-base64":
            rules.add(arg, is_base64=True)
    obj = AdblockPlus2Lists(rules, ignore_path=True)
    result: Result = obj.convert()
    if output_file:
        with open(output_file, "w") as ouf:
            result.write_surge(file=ouf)
    else:
        result.write_surge()
    result.print_statistics()


if __name__ == '__main__':
    main(sys.argv[1:])
