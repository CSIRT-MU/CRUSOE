from math import inf


class StdoutPrinter:
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

    def __init__(self, limit, verbose):
        self.limit = limit
        self.verbose = verbose
        self.headers = ["IP ADDRESS", "DOMAIN(S)", "RISK"]
        self.widths = [20, 0, 10]

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

        # Get shortened list if limit is given
        # List slices doesn't work with none -> use inf instead of None
        list_slice = host_list[:self.limit]

        # Get maximum domain name length a set it as a width for domain column
        self.widths[1] = self.__find_longest_domain(list_slice) + 2

        # Use verbose print
        if self.verbose:
            self.headers.append("SIMILARITIES")
            self.widths.append(self.__find_longest_warning(list_slice) + 2)

        table_color = self.YELLOW

        # Print table header
        self.__print_host_list_header(self.BLUE)

        # Print table
        self.__print_horizontal_separator(table_color)

        for host in list_slice:
            self.__print_host_in_table(host, table_color)
            self.__print_horizontal_separator(self.YELLOW)

    @staticmethod
    def __find_longest_domain(host_list):
        longest = 0

        for host in host_list:
            current_longest = len(max(host.domains, key=lambda x: len(x)))
            if current_longest > longest:
                longest = current_longest

        return longest

    @staticmethod
    def __find_longest_warning(host_list):
        longest = 0

        for host in host_list:
            if host.warnings:
                current_longest = \
                    len(str(max(host.warnings, key=lambda x: len(str(x)))))
                if current_longest > longest:
                    longest = current_longest

        return longest

    def __print_horizontal_separator(self, color):
        print(color, end="")
        for width in self.widths:
            print(f"+{width * '-'}", end="")
        print("+" + self.END)

    def __print_host_list_header(self, color):
        print(color + self.BOLD, end="")
        for header, width in zip(self.headers, self.widths):
            print(" " + str.center(header, width), end="")
        print(self.END)

    def __print_host_in_table(self, host, color):
        print(color + "|", end="")

        print_items = [str(host.ip), host.domains[0],
                       str(round(host.risk, 4))]

        if self.verbose and host.warnings:
            print_items.append(str(host.warnings[0]))
        elif self.verbose:
            print_items.append("")

        for item, width in zip(print_items, self.widths):
            print(self.YELLOW + str.center(item, width) + "|", end="")

        # Print domains and warnings, which can take more rows
        if len(host.domains) > 1 or (len(host.warnings) > 1 and self.verbose):
            print()

            # One row is already printed -> minus one
            if self.verbose:
                rows = max(len(host.domains), len(host.warnings)) - 1
            else:
                rows = len(host.domains)

            for i in range(1, rows + 1):
                # IP
                print("|" + self.widths[0] * " " + "|", end="")

                # DOMAIN
                if i < len(host.domains):
                    print(str.center(host.domains[i], self.widths[1]) + "|", end="")
                else:
                    print(self.widths[1] * " " + "|", end="")

                # RISK
                print(self.widths[2] * " " + "|", end="")

                # WARNINGS
                if self.verbose and i < len(host.warnings):
                    print(str.center(str(host.warnings[i]),
                                     self.widths[3]) + "|")
                elif self.verbose:
                    print(self.widths[3] * " " + "|")
                else:
                    print()
        else:
            print()

        print(self.END, end="")


