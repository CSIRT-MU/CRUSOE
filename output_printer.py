from math import inf

class OutputPrinter:
    # ASCII text edit symbols
    PINK = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    HEADERS = ["IP ADDRESS", "DOMAIN(S)", "RISK"]

    WIDTHS = [20, 50, 10]

    def __init__(self, limit, verbose):
        self.limit = limit
        self.verbose = verbose

    def print_attacked_host(self, host):
        print(self.BLUE + self.BOLD + "ATTACKED HOST:" + self.END)
        print(host)

    def print_number_of_hosts(self, number_of_hosts, max_distance):
        print(self.BLUE +
              f"Found {number_of_hosts} hosts to maximum distance of "
              f"{max_distance}:")
        # Show how much hosts is actually being printed (defined by limit
        # given as a option)
        if self.limit is not None and self.limit < number_of_hosts:
            print(self.BLUE +
                  f"Displaying {self.limit} hosts.")
        print()

    def print_host_list(self, host_list):
        """
        Prints given host list to stdout formatted in a table.
        :param host_list: List of hosts to print
        :return: None
        """
        table_color = self.YELLOW

        # Print table header
        self.__print_host_list_header(self.BLUE)

        # Print table
        self.__print_horizontal_separator(table_color)

        # List slices doesn't work with none -> use inf instead of None
        for host in host_list[:inf if self.limit is None else self.limit]:
            self.__print_host_in_table(host, table_color)
            self.__print_horizontal_separator(self.YELLOW)

    def __print_horizontal_separator(self, color):
        print(color, end="")
        for width in self.WIDTHS:
            print(f"+{width * '-'}", end="")
        print("+" + self.END)

    def __print_host_list_header(self, color):
        print(color + self.BOLD, end="")
        for header, width in zip(self.HEADERS, self.WIDTHS):
            print(" " + str.center(header, width), end="")
        print(self.END)

    def __print_host_in_table(self, host, color):
        print(color + "|", end="")

        for item, width in [(str(host.ip), 20), (host.domains[0], 50),
                            (str(round(host.risk, 4)), 10)]:
            print(self.YELLOW + str.center(item, width) + "|", end="")
        if len(host.domains) > 1:
            print()
            for domain in host.domains[1:]:
                print("|" + 20 * " " + "|", end="")
                print(str.center(domain, 50), end="")
                print("|" + 10 * " " + "|")
        else:
            print()

        print(self.END, end="")


