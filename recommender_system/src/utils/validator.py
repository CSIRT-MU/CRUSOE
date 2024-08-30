from ipaddress import ip_address
from re import match


class Validator:
    """
    Static class with helper methods for validating input.
    """

    @staticmethod
    def validate_ip(ip):
        """
        Checks if given string is a valid IP address.
        :param ip: IP address in a form of a string
        :return: True if given string is correct IP, False otherwise
        """
        try:
            ip_address(ip)
        except ValueError:
            return False

        return True

    @staticmethod
    def validate_domain(domain):
        """
        Checks if given string is a valid domain name.
        Regex obtained from:
        https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch08s15.html
        :param domain: Domain name to be checked
        :return: Bool (True - correct domain, False - otherwise)
        """
        if match(r"^((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+["
                 "a-z]{2,63}.?$", domain) is None:
            return False

        return True

    @staticmethod
    def validate_positive_integer(num):
        """
        Checks if given number is a positive integer number.
        :param num: Number
        :return: True if correct positive integer was given, false otherwise
        """
        try:
            num = int(num)
        except ValueError:
            return False

        if num <= 0:
            return False

        return True
