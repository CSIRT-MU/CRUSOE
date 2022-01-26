class SoftwareComponent:
    """
    Represents software running on a host.
    """
    def __init__(self, tag, cpe):
        self.tag = tag
        self.cpe_list = cpe.split(":")

    @property
    def vendor(self):
        return self.cpe_list[0] if len(self.cpe_list) > 0 else None

    @property
    def product(self):
        return self.cpe_list[1] if len(self.cpe_list) > 1 else None

    @property
    def version(self):
        return self.cpe_list[2] if len(self.cpe_list) > 2 else None

    def __str__(self):
        return f"{self.tag}: {self.vendor}:{self.product}:{self.version}"

    def to_json(self):
        return {
            "vendor": self.vendor,
            "product": self.product,
            "version": self.version
        }
