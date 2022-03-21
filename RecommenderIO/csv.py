class CsvOutput:
    #TODO add documentation
    @staticmethod
    def csv_export(host_list, verbose, file_path):
        with open(file_path, "w") as writer:
            rows = ""
            for host in host_list:
                rows += host.to_csv(verbose) + "\n"
            writer.write(rows)
