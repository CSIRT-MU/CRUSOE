class CsvOutput:
    """
    Exports recommender script output in CSV file.
    """
    @staticmethod
    def csv_export(host_list, file_path):
        """
        Exports recommended host list in a CSV file.
        :param host_list: List of recommended hosts
        :param file_path: Path to CSV file
        :return: None
        """
        with open(file_path, "w") as writer:
            rows = ""
            for host in host_list:
                rows += host.to_csv() + "\n"
            writer.write(rows)
