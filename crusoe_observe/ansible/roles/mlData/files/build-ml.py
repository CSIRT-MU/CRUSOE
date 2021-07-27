import sys
import structlog

from osrest import Tcpml
import services_component

def build_os(dataset_path, model_path, logger):
    logger.info(f"Loading OS dataset from \"{dataset_path}\".")
    dataset = Tcpml.load_dataset(dataset_path)
    logger.info(f"Building OS model.")
    model = Tcpml.build_model(dataset)
    logger.info(f"Storing OS model to \"{model_path}\".")
    Tcpml.save_model(model, model_path)

def build_si(dataset_path, model_path, logger):
    paths = {
        "model": model_path,
        "dataset": dataset_path,
        "nbar": f"{services_component.__path__[0]}/data/si_nbar.json"
    }

    si = services_component.services.ServiceIdentifier(paths, ["0.0.0.0/0"], logger)

def main():
    ml_data_path = sys.argv[1]
    ml_model_path = sys.argv[2]

    logger = structlog.PrintLogger()

    logger.info("Starting OS model build.")
    build_os(f"{ml_data_path}os_dataset.csv", f"{ml_model_path}os_model.pkl", logger)
    logger.info("Finishing OS model build.")
    logger.info("Starting SI model build.")
    build_si(f"{ml_data_path}si_dataset.csv", f"{ml_model_path}si_model.pkl", logger)
    logger.info("Finishing SI model build.")

if __name__ == "__main__":
    main()
