class StdoutPrinter:
    """
    Prints result of the recommender script to the standard output in a
    formatted way.
    """

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
        self.__headers = ["IP ADDRESS", "DOMAIN(S)", "CONTACT(S)", "RISK"]
        self.__widths = [20, 0, 0, 24]

    def print_attacked_host(self, host, header_color=BLUE, color=END):
        """
        Prints information about attacked host.
        :param host: Attacked host
        :param header_color: Color of the header
        :param color: Color of the host's attributes
        :return: None
        """
        print(header_color + "ATTACKED HOST:" + self.END)
        print(color + str(host) + self.END)
        print()

    def print_number_of_hosts(self, number_of_hosts, color=END):
        """
        Prints information about number of nearby hosts find and number
        of hosts actually given to stdout (in case limit option is used.
        :param number_of_hosts: Number of hosts found
        :param color: Color of the result string
        :return: None
        """

        print(color +
              f"Found {number_of_hosts} hosts." + self.END)

        # Show how many hosts is actually being printed (defined by limit
        # given as a option)
        if self.limit is not None and self.limit < number_of_hosts:
            print(color + f"Displaying {self.limit} hosts." + self.END)
        print()

    def print_host_list(self, host_list, header_color=BLUE, color=END):
        """
        Prints given host list to stdout formatted in a table.
        :param host_list: List of hosts to print
        :param header_color: Color of the header
        :param color: Color of the header
        :return: None
        """

        if not host_list:
            return

        # Get shortened list if limit is given
        list_slice = host_list[:self.limit]

        # Verbose print
        if self.verbose:
            self.__headers.append("SIMILARITIES")
            self.__widths.append(0)

        # Calculate width for variable size columns
        self.__calc_column_widths(host_list)

        # Print table header
        self.__print_host_list_header(header_color)

        # Print table
        self.__print_horizontal_separator(color)

        for host in list_slice:
            self.__print_host_in_table(host, color)
            self.__print_horizontal_separator(color)

    def __calc_column_widths(self, host_list):
        """
        Calculates width of all columns - it finds widest value in each
        column and adds 2 (value plus two spaces).
        :param host_list: List of hosts for printing
        :return: None
        """

        len_contact = 0
        len_domain = 0
        len_warning = 0

        for host in host_list:
            current_longest = 1
            # Domain
            if len(host.domains) > 0:
                current_longest = len(max(host.domains, key=lambda x: len(x)))
                len_domain = max(current_longest, len_domain)

            # Contact
            if len(host.contacts) > 0:
                current_longest = len(max(host.contacts, key=lambda x: len(x)))
                len_contact = max(current_longest, len_contact)

            # Warnings
            if self.verbose:
                if len(host.warnings) > 0:
                    current_longest = \
                        len(str(max(host.warnings, key=lambda x: len(str(x)))))
                    len_warning = max(current_longest, len_warning)

        # Set widths (+ 2 -> margin from a table, looks better)
        self.__widths[1] = len_domain + 2
        self.__widths[2] = len_contact + 2
        if self.verbose:
            self.__widths[4] = len_warning + 2

    def __print_horizontal_separator(self, color):
        """
        Prints horizontal separator of a table in given color.
        :param color: Color of a separator as ASCII edit symbol
        :return: None
        """
        print(color, end="")
        for width in self.__widths:
            print(f"+{width * '-'}", end="")
        print("+" + self.END)

    def __print_host_list_header(self, color):
        """
        Prints header of host list in given color.
        :param color: Header color as ASCII edit symbol
        :return: None
        """
        print(color, end="")
        for header, width in zip(self.__headers, self.__widths):
            print(" " + str.center(header, width), end="")
        print(self.END)

    def __print_host_in_table(self, host, color):
        """
        Prints one host in a result table in given color.
        :param host: Host object to be printed
        :param color: Color of a row with host as ASCII edit symbol
        :return: None
        """

        print(color + "|", end="")

        domain = host.domains[0] if len(host.domains) > 1 else "Not found"
        contact = host.contacts[0] if len(host.contacts) > 1 else "Not found"

        print_items = [str(host.ip), domain, contact,
                       '{:.20f}'.format(host.risk)]

        if self.verbose and host.warnings:
            print_items.append(str(host.warnings[0]))
        elif self.verbose:
            print_items.append("")

        for item, width in zip(print_items, self.__widths):
            print(color + str.center(item, width) + "|", end="")

        # Print domains and warnings, which can take more rows
        if len(host.domains) > 1 or len(host.contacts) or \
                (len(host.warnings) > 1 and self.verbose):
            print()

            # One row is already printed -> minus one
            if self.verbose:
                rows = max(max(len(host.domains), len(host.warnings)),
                           len(host.contacts)) - 1
            else:
                rows = max(len(host.domains), len(host.contacts)) - 1

            for i in range(1, rows + 1):
                # IP
                print("|" + self.__widths[0] * " " + "|", end="")

                # DOMAIN
                if i < len(host.domains):
                    print(str.center(host.domains[i], self.__widths[1]) + "|",
                          end="")
                else:
                    print(self.__widths[1] * " " + "|", end="")

                # CONTACT
                if i < len(host.contacts):
                    print(str.center(host.contacts[i], self.__widths[2]) + "|",
                          end="")
                else:
                    print(self.__widths[2] * " " + "|", end="")

                # RISK
                print(self.__widths[3] * " " + "|", end="")

                # WARNINGS
                if self.verbose and i < len(host.warnings):
                    print(str.center(str(host.warnings[i]),
                                     self.__widths[4]) + "|")
                elif self.verbose:
                    print(self.__widths[4] * " " + "|")
                else:
                    print()
        else:
            print()

        print(self.END, end="")
