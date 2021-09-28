#!/usr/bin/env python
from db_connection import DatabaseConnection


def main():
    bolt_url = "bolt://localhost:7687"
    user = "neo4j"
    password = open("pass", mode='r').read()
    app = DatabaseConnection(bolt_url, user, password)
    print(app.find_and_resolve_domain("disa.fi.muni.cz"))
    app.close()


if __name__ == "__main__":
    main()
