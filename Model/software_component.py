class SoftwareComponent:
    """
    Represents software running on a host.
    """
    def __init__(self, tag, cpe):
        self.tag = tag

        if cpe is not None:
            cpe_split = cpe.split(":", 3)
            self.vendor = cpe_split[0]
            self.product = cpe_split[1]

            if len(cpe_split) > 2:
                self.version = cpe_split[2]
        else:
            self.vendor = None
            self.product = None
            self.version = None

    def __str__(self):
        return f"{self.tag}: {self.vendor}:{self.product}:{self.version}"
