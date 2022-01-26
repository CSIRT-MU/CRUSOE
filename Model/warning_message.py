class WarningMessage:
    """
    Partial similarity with high score that should be displayed
    on output with comment what is causing the similarity.
    """
    def __init__(self, message, similarity_score):
        self.message = message
        self.similarity_score = similarity_score

    def __str__(self):
        return f"{self.message} : {self.similarity_score}"
