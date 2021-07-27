"""Core module provides core functionality for services component for managing
detected service and its versions. It should provide uniform solution for
handling them and simplify interactions between different methods and
subcomponents.
"""


def cpe(*args):
    """Concatenate values as strings using ':', replace None with '*'
    :param args: sequence of values
    :return: string in CPE format
    """
    return ":".join(map(lambda x: "*" if x is None else str(x), args))


def cpe_vendor(vendor=None):
    """Shorthand for generator of vendor subpart of CPE string
    :param vendor: vendor
    :return: string in format vendor
    """
    return cpe(vendor)


def cpe_product(vendor=None, product=None):
    """Shorthand for generator of vendor:product subpart of CPE string
    :param vendor: vendor
    :param product: product
    :return: string in format vendor:product
    """
    return cpe(vendor, product)


def cpe_version(vendor=None, product=None, version=None):
    """Shorthand for generator of vendor:product:version subpart of CPE string
    :param vendor: vendor
    :param product: product
    :param version: version
    :return: string in format vendor:product:version
    """
    return cpe(vendor, product, version)


class Version:
    """This class represents (CPE) version in the service hierarchy"""

    def __init__(self, name):
        self.name = name
        self.counter = 0

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Version<{self.name},{self.counter}>"

    def inc(self, by=1):
        """Increase the value of counter by given amount
        :param by: the amount to increase by
        """
        self.counter += by

    def total(self):
        """Get the total sum of counters on this item and its subordinates in the hierarchy.
        :return: the total sum
        """
        return self.counter

    def current(self):
        """Get value of counter of self
        :return: the value of self.counter
        """
        return self.counter

    def most(self):
        """Get pair of the path with the highest sum of counters and the sum.
        :return: (counter_sum, path_with_highest_counter_sum)
        """
        if self.counter <= 0:
            return self.counter, [None]
        return self.counter, [self.name]

    def all(self):
        """Get pairs of all paths and sum of their counters.
        :return: list of (counter_sum, path) pairs
        """
        if self.counter <= 0:
            return []
        return [(self.counter, [self.name])]

    def merge(self, other, weight=1):
        """Merge with another object of the same level in the hierarchy
        :param other: other object of the same level in the hierarchy
        :param weight: coefficient of values of the merged (other) object
        """
        self.counter += other.counter * weight

    def normalize(self, total=None):
        """Divide values of all counters by value of total
        :param total: number to divide by; if unspecified self.total() is used
        """
        total = self.total() if total is None else total
        if total == 0:
            total = 1
        self.counter /= total


class Product:
    """This class represents (CPE) product in the service hierarchy"""

    def __init__(self, name):
        self.name = name
        self.counter = 0
        self.items = {}

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Product<{self.name},{self.counter}> {repr(self.items)}"

    def __getitem__(self, key):
        if key is None:  # TODO wrapper object that disables subsequential [] calls
            return self
        result = self.items.get(key)
        if result is None:
            result = Version(key)
            self.items[key] = result
        return result

    def inc(self, by=1):
        """Increase the value of counter by given amount
        :param by: the amount to increase by
        """
        self.counter += by

    def total(self):
        """Get the total sum of counters on this item and its subordinates in the hierarchy.
        :return: the total sum
        """
        return self.counter + sum(map(lambda x: x.total(), self.items.values()))

    def current(self):
        """Get value of counter of self
        :return: the value of self.counter
        """
        return self.counter

    def prune(self):
        """Prune subordinate items (if their total() is 0, delete them)"""
        to_delete = []
        for item in self.items:
            if self.items[item].total() == 0:
                to_delete.append(item)
        for item in to_delete:
            del self.items[item]

    def most(self):
        """Get pair of the path with the highest sum of counters and the sum.
        :return: (counter_sum, path_with_highest_counter_sum)
        """
        default = (0, [None])
        num, path = max(map(lambda x: x.most(), self.items.values()), default=default, key=lambda x: x[0])
        if num + self.counter <= 0:
            return default[0], [None] + default[1]
        return num + self.counter, [self.name] + path

    def all(self):
        """Get pairs of all paths and sum of their counters.
        :return: list of (counter_sum, path) pairs
        """
        sub = sum(map(lambda x: x.all(), self.items.values()), [])
        if len(sub) == 0:
            if self.counter <= 0:
                return []
            else:
                sub = [(0, [None])]
        return list(map(lambda x: (self.counter + x[0], [self.name] + x[1]), sub))

    def merge(self, other, weight=1):
        """Merge with another object of the same level in the hierarchy
        :param other: other object of the same level in the hierarchy
        :param weight: coefficient of values of the merged (other) object
        """
        self.counter += other.counter * weight
        for key in other.items:
            self[key].merge(other[key], weight)

    def normalize(self, total=None):
        """Divide values of all counters by value of total
        :param total: number to divide by; if unspecified self.total() is used
        """
        total = self.total() if total is None else total
        if total == 0:
            total = 1
        self.counter /= total
        for item in self.items.values():
            item.normalize(total)


class Vendor:
    """This class represents (CPE) vendor in the service hierarchy"""

    def __init__(self, name):
        self.name = name
        self.counter = 0
        self.items = {}

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Vendor<{self.name},{self.counter}> {repr(self.items)}"

    def __getitem__(self, key):
        if key is None:  # TODO wrapper object that disables subsequential [] calls
            return self
        result = self.items.get(key)
        if result is None:
            result = Product(key)
            self.items[key] = result
        return result

    def inc(self, by=1):
        """Increase the value of counter by given amount
        :param by: the amount to increase by
        """
        self.counter += by

    def total(self):
        """Get the total sum of counters on this item and its subordinates in the hierarchy.
        :return: the total sum
        """
        return self.counter + sum(map(lambda x: x.total(), self.items.values()))

    def all(self):
        """Get pairs of all paths and sum of their counters.
        :return: list of (counter_sum, path) pairs
        """
        sub = sum(map(lambda x: x.all(), self.items.values()), [])
        if len(sub) == 0:
            if self.counter <= 0:
                return []
            else:
                sub = [(0, [None, None])]
        return list(map(lambda x: (self.counter + x[0], [self.name] + x[1]), sub))

    def current(self):
        """Get value of counter of self
        :return: the value of self.counter
        """
        return self.counter

    def prune(self):
        """Prune subordinate items (if their total() is 0, delete them)"""
        to_delete = []
        for item in self.items:
            if self.items[item].total() == 0:
                to_delete.append(item)
        for item in to_delete:
            del self.items[item]

    def most(self):
        """Get pair of the path with the highest sum of counters and the sum.
        :return: (counter_sum, path_with_highest_counter_sum)
        """
        default = (0, [None, None])
        num, path = max(map(lambda x: x.most(), self.items.values()), default=default, key=lambda x: x[0])
        if num + self.counter <= 0:
            return default[0], [None] + default[1]
        return num + self.counter, [self.name] + path

    def merge(self, other, weight=1):
        """Merge with another object of the same level in the hierarchy
        :param other: other object of the same level in the hierarchy
        :param weight: coefficient of values of the merged (other) object
        """
        self.counter += other.counter * weight
        for key in other.items:
            self[key].merge(other[key], weight)

    def normalize(self, total=None):
        """Divide values of all counters by value of total
        :param total: number to divide by; if unspecified self.total() is used
        """
        total = self.total() if total is None else total
        if total == 0:
            total = 1
        self.counter /= total
        for item in self.items.values():
            item.normalize(total)


class Hierarchy:
    """This class represents root object for managing the service hierarchy.
    Typically associated with specific device (IP).
    """

    def __init__(self):
        self.counter = 0
        self.items = {}

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Hierarchy<{self.counter}> {repr(self.items)}"

    def __getitem__(self, key):
        if key is None: # TODO wrapper object that disables subsequential [] calls
            return self
        result = self.items.get(key)
        if result is None:
            result = Vendor(key)
            self.items[key] = result
        return result

    def inc(self, by=1):
        """Increase the value of counter by given amount
        :param by: the amount to increase by
        """
        self.counter += by

    def total(self):
        """Get the total sum of counters on this item and its subordinates in the hierarchy.
        :return: the total sum
        """
        return self.counter + sum(map(lambda x: x.total(), self.items.values()))

    def current(self):
        """Get value of counter of self
        :return: the value of self.counter
        """
        return self.counter

    def prune(self):
        """Prune subordinate items (if their total() is 0, delete them)"""
        to_delete = []
        for item in self.items:
            if self.items[item].total() == 0:
                to_delete.append(item)
        for item in to_delete:
            del self.items[item]

    def most(self):
        """Get pair of the path with the highest sum of counters and the sum.
        :return: (counter_sum, path_with_highest_counter_sum)
        """
        default = (0, [None, None, None])
        num, path = max(map(lambda x: x.most(), self.items.values()), default=default, key=lambda x: x[0])
        if num + self.counter <= 0:
            return default[0], default[1]
        return num + self.counter, path

    def all(self):
        """Get pairs of all paths and sum of their counters.
        :return: list of (counter_sum, path) pairs
        """
        sub = sum(map(lambda x: x.all(), self.items.values()), [])
        if len(sub) == 0:
            if self.counter <= 0:
                return []
            else:
                sub = [(0, [None, None, None])]
        return list(map(lambda x: (self.counter + x[0], x[1]), sub))

    def merge(self, other, weight=1):
        """Merge with another object of the same level in the hierarchy
        :param other: other object of the same level in the hierarchy
        :param weight: coefficient of values of the merged (other) object
        """
        self.counter += other.counter * weight
        for key in other.items:
            self[key].merge(other[key], weight)

    def normalize(self, total=None):
        """Divide values of all counters by value of total
        :param total: number to divide by; if unspecified self.total() is used
        """
        total = self.total() if total is None else total
        if total == 0:
            total = 1
        self.counter /= total
        for item in self.items.values():
            item.normalize(total)


class Result:
    """Class for managing IPs of observed devices and their service service hierarchies"""

    def __init__(self):
        self.items = {}  # IP (Hierarchy) -> Vendor -> Product -> Version

    def __getitem__(self, key):
        if key is None:
            raise KeyError("\"None\" supplied as key for Result object")

        result = self.items.get(key)
        if result is None:
            result = Hierarchy()
            self.items[key] = result
        return result

    def normalize(self):
        """Normalize values of the Result, so the sum is 1 for each IP
        """
        for item in self.items.values():
            item.normalize()

    def merge(self, other, weight=1):
        """Merge with another object of the same level in the hierarchy
        :param other: other object of the same level in the hierarchy
        :param weight: coefficient of values of the merged (other) object
        """
        for key in other.items:
            self[key].merge(other[key], weight)

    def finalize(self, category, exclusive=True):
        """Format results into JSON objects output list annotated by category
        :param category: category of the result
        :param exclusive: pick only the stronges result in each hierarchy
        :return: list of JSON objects representing the findings
        """
        final = []
        for ip in self.items:
            if exclusive:
                matches = [self[ip].most()]
            else:
                self[ip].prune()
                matches = self[ip].all()
            matches = map(lambda x: x[1], matches)
            for match in matches:
                final.append({
                    "ip": ip,
                    "vendor": match[0],
                    "product": match[1],
                    "type": category,
                    "name": cpe(*match[0:2]),
                    "version": cpe(*match)
                })
        return final

    def prune(self):
        """Prune hierarchies (if their total() is 0, delete them)"""
        for item in self.items:
            if self.items[item].total() == 0:
                del self.items[item]
            else:
                self.items[item].prune()

    def count(self):
        """Return the number of IP which had some service detected
        :return: the number of IP which had some service detected
        """
        return len(self.items.keys())
