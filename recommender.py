#!/usr/bin/env python
from db_connection import DatabaseConnection
from input import Input


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

    db_connection.close()


if __name__ == "__main__":
    main()
