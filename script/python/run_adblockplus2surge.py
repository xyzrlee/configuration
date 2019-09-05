from adblockplus2surge import AdblockPlus2Surge
import getopt
import sys


def main(argv) -> None:
    output_file = None
    rules = []
    opts, args = getopt.getopt(argv, "", ["output-file=", "abp-rule="])
    for opt, arg in opts:
        if opt == "--output-file":
            output_file = arg
        elif opt == "--abp-rule":
            rules.append(arg)
    obj = AdblockPlus2Surge(set(rules))
    obj.convert(output_file)


if __name__ == '__main__':
    main(sys.argv[1:])
