#!/usr/bin/env python
from sys import argv
from getopt import getopt, GetoptError
from db_connection import DatabaseConnection


class Input:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    @staticmethod
    def parse_arguments():
        ip = ""
        domain = ""

        try:
            # -i | --ip     -> IP input
            # -d | --domain -> domain input
            opts, _ = getopt(argv[1:], "i:d:", ["ip=", "domain="])

        except GetoptError:
            print("Error - Invalid options")
            return False

        if not opts:
            # No options were obtained
            print("Error - No arguments were given")
            return False

        for opt, arg in opts:
            if opt in ("-i", "--ip"):
                ip = arg
            elif opt in ("-d", "--domain"):
                domain = arg

        print(ip + " " + domain)

