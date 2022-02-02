class WarningMessage:
    """
    Represents partial similarity with high score that should be displayed
    on output with reason what is causing the similarity.
    """
    def __init__(self, message, similarity_score):
        self.message = message
        self.similarity_score = similarity_score

    def __str__(self):
        return f"{self.message} : {round(self.similarity_score, 4)}"

    def to_json(self):
        return {
            "message": self.message,
            "partial_similarity": self.similarity_score
        }
