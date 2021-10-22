#!/usr/bin/env python
from db_connection import DatabaseConnection
from input import Input
import time


def main():
    bolt_url = "bolt://localhost:7687"
    user = "neo4j"
    password = open("pass", mode='r').read()
    db_connection = DatabaseConnection(bolt_url, user, password)

    input_parser = Input()

    if input_parser.parse_options():
        if input_parser.ip is not None:
            attacked_host = db_connection.get_host_by_ip(input_parser.ip)
        else:
            attacked_host = \
                db_connection.get_host_by_domain(input_parser.domain)

        print(attacked_host)

        host_list = db_connection.find_close_hosts(str(attacked_host.ip), 4)

    db_connection.close()


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
