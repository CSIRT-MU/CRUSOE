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

    HEADERS = [
        ("IP ADDRESS", 20),
        ("DOMAIN(S)", 50),
        ("RISK", 10)
    ]

    def __init__(self, limit, verbose):
        self.column_width = 40
        # Set limit to infinity if no limit was given from options
        self.limit = inf if limit is None else limit
        self.verbose = verbose

    def print_number_of_hosts(self, number_of_hosts, max_distance):
        print()
        print(self.BLUE +
              f"Found {number_of_hosts} hosts to maximum distance of "
              f"{max_distance}:")
        if self.limit < inf:
            print(self.BLUE +
                  f"Displaying {self.limit} hosts.")
        print()

    def print_host_list(self, host_list):
        # Print headers
        print(self.GREEN + " ", end="")
        for header, width in self.HEADERS:
            print(self.BOLD + self.BLUE + str.center(header, width) + " ",
                  end="")
        print(self.END)

        # Print host list
        for host in host_list[:self.limit]:  # Limit number of
            print(self.YELLOW + "|", end="")

            for item, width in [(str(host.ip), 20), (host.domains[0], 50), (str(round(host.risk, 4)), 10)]:
                print(self.YELLOW + str.center(item, width) + "|", end="")
            print()

    def print_attacked_host(self, host):
        print(self.BLUE + self.BOLD + "ATTACKED HOST:" + self.END)
        print(host)
