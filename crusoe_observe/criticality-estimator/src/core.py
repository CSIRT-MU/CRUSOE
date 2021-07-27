"""
criticality_estimator is a component that provides an interface for
requesting computations on database with the goal of estimation of criticality
of certain nodes, and returning information about the computations.
"""

import structlog
from neo4jclient import CriticalityClient


class CriticalityEstimator:
    """CriticalityEstimator class comprises essential functionality for
    logging, connection to database, sending queries through CriticalityClient,
    and returning information about the computations in readable format.
    """

    def __init__(self, bolt="bolt://localhost:7687", password="test", logger=structlog.get_logger()):
        """Create an instance of CriticalityEstimator, connect to database, store logger
        :param bolt: bolt address
        :param password: password to database
        :param logger: logger instance to use for logging
        """
        self.logger = logger
        self.db = CriticalityClient(bolt=bolt, password=password)
        self.logger.info("Initialized")

    def run(self):
        """Run CriticalityEstimator
        :return: result mesage
        """
        self.logger.info("Start")
        topology_result = self.compute_topology()
        dependency_result = self.compute_dependency()
        self.logger.info("Finish")
        return f"Criticality: {topology_result}; {dependency_result}."

    def compute_topology(self):
        """Perform CriticalityEstimator topology computations on database
        :return: result message
        """
        self.logger.info("Start topology betweenness")
        result = self.compute_topology_betweenness()
        betweenness_result = {
            "nodes": result["nodes"],
            "load_ms": result["loadMillis"],
            "compute_ms": result["computeMillis"],
            "write_ms": result["writeMillis"],
        }
        self.logger.info("Finish topology betweenness", **betweenness_result)
        self.logger.info("Start topology degree")
        result = self.compute_topology_degree()
        degree_result = {
            "nodes": result["nodes"],
            "load_ms": result["loadMillis"],
            "compute_ms": result["computeMillis"],
            "write_ms": result["writeMillis"],
        }
        self.logger.info("Finish topology degree", **degree_result)
        return f"topology betweenness {betweenness_result['nodes']} nodes; " \
               f"topology degree {degree_result['nodes']} nodes"

    def compute_topology_betweenness(self):
        """Perform topology betweenness computation
        :return: computation information
        """
        result = self.db.compute_topology_betweenness()
        return result.data()[0]

    def compute_topology_degree(self):
        """Perform topology degree computation
        :return: computation information
        """
        result = self.db.compute_topology_degree()
        return result.data()[0]

    def compute_dependency(self):
        """Perform CriticalityEstimator dependency computations on database
        :return: result message
        """
        self.logger.info("Start dependency degree")
        result = self.compute_dependency_degree()
        degree_result = {
            "nodes": result["nodes"],
            "load_ms": result["loadMillis"],
            "compute_ms": result["computeMillis"],
            "write_ms": result["writeMillis"],
        }
        self.logger.info("Finish dependency degree", **degree_result)
        return f"dependency degree {degree_result['nodes']} nodes"

    def compute_dependency_degree(self):
        """Perform dependency degree computation
        :return: computation information
        """
        result = self.db.compute_dependency_degree()
        return result.data()[0]
