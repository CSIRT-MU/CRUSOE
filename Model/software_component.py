class SoftwareComponent:
    """
    Represents software running on a host.
    """
    def __init__(self, tag, cpe):
        self.tag = tag
        self.cpe = cpe

    def __str__(self):
        return f"{self.tag}: {self.cpe}"
