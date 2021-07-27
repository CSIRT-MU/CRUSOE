"""Utils module contains utility functions for services_component and its submodules
"""
import re
import collections.abc


range_regex = re.compile("([0-9]+)((,[0-9]+)?\.\.([0-9]+))?")


def any_match(record, patterns):
    """Check record for match with any of the patterns
    :param record: record string to search for patterns
    :param patterns: list of regexes
    :return: True of record matched with any of the patterns; False otherwise
    """
    return any(map(lambda x: x.search(record), patterns))


def compile_regexes(regexes):
    """Compile regexes and return them in a list
    :param regexes: either single regex, or a list of them
    :return: list of compiled regexes
    """
    if isinstance(regexes, collections.abc.Iterable) and not isinstance(regexes, str):
        return list(map(re.compile, regexes))
    return [re.compile(regexes)]


def parse_range(range_str):
    """Parses range from a string
    :param range_str: range in a form of a string
    :return: range object parsed from the string
    """
    match = range_regex.match(range_str)
    if match:
        groups = match.groups()
        start = int(groups[0])
        end = int(groups[3]) if groups[3] else start + 1
        if groups[1] and groups[2]:
            step = int(groups[2][1:]) - start
            return range(start, end, step)

        return range(start, end)

    raise ValueError
