import getopt
import os
import sys

from adblockplus2lists import AdblockPlus2Lists, Result, Rules


def main(argv) -> None:
    output_file = None
    type = "list"
    rules = Rules()
    opts, args = getopt.getopt(argv, "", ["output-file=", "abp-rule=", "type="])
    for opt, arg in opts:
        if opt == "--output-file":
            output_file = arg
        elif opt == "--abp-rule":
            rules.add(arg)
        elif opt == "--type":
            type = arg
    obj = AdblockPlus2Lists(rules)
    result: Result = obj.convert()
    print("%s" % os.path.abspath(output_file))
    with open(output_file, "w") as ouf:
        if type == "list":
            result.write_surge(file=ouf)
        elif type == "set":
            result.write_surge_domain_set(file=ouf)
    result.print_statistics()


if __name__ == '__main__':
    main(sys.argv[1:])
