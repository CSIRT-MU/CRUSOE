# CRUSOE

## A Toolset for Cyber Situational Awareness and Decision Support in Incident Handling Inspired by the OODA Loop

### About

The growing size and complexity of today's computer network make it hard to achieve and maintain so-called cyber situational awareness, i.e., the ability to perceive and comprehend the cyber environment and be able to project the situation in the near future. Namely, CSIRT/CERT or SOC personnel should be aware of the security situation in the network to effectively prevent or mitigate cyber attacks and avoid mistakes in the process. Herein, we present a toolset for achieving cyber situational awareness in a large and heterogeneous environment. The goal of the toolset is to support cybersecurity teams in iterating through the OODA loop (Observe, Orient, Decide, Act). The tool was designed to help the operator make informed decisions in incident handling and response for each phase of the cycle. The Observe phase builds on common tools for active and passive network monitoring and vulnerability assessment. In the Orient phase, the data on the network are structured and presented in a comprehensible and visually appealing manner. The Decide phase is represented by a recommender system that suggests the most resilient configuration of the critical infrastructure. Finally, the Act phase is supported by a service that orchestrates network security tools and allows for prompt mitigation actions.

![Architecture of the CRUSOE Toolset](/crusoe-architecture.png "Architecture of the CRUSOE toolset")

### Original Source Codes

The tools as at the end of the CRUSOE project are available at the repository of Masaryk University.  
Observe: https://www.muni.cz/en/research/publications/1724696  
Orient: https://www.muni.cz/en/research/publications/1724716  
Decide: https://www.muni.cz/en/research/publications/1724737  
Act: https://www.muni.cz/en/research/publications/1728677  

### Installation

The software is modular and can be installed either in parts, or as a whole using Ansible. For installation instructions of each separate tool or component, see readme.md files in the corresponding subfolders.

### Datasets

In the "datasets" directory, you can find a sample dataset to work with if you do not your own data or just want to try CRUSOE. At the moment, there is a dump of Neo4j database filled with data from the Cyber Czech excercise in KYPO cyber range. Raw data can be found on Zenodo: https://zenodo.org/records/3746129

To use the data, turn your Neo4j instance off and overwrite the content of your database with the dump using the command: neo4j-admin load --from .dump --database=neo4j --force

Thanks goes to Lukáš Sadlek for preparing the dataset.

### Documentation

The "documentation" directory contains four documents describing the design and implementation of the four components of the original CRUSOE toolset. The documents were originally written in Czech language and later translated using DeepL. Original documents are available in the same repository as the original source codes (see the links above).

### Authors

The authors of the CRUSOE toolset are:

Martin Laštovička, Jakub Bartoloměj Košuth, Danei Filakovský, and Martin Husák (Observe tool)  
Lukáš Matta and Martin Husák (Orient tool)  
Lukáš Sadlek, Michal Javorník, and Martin Husák (Decide tool)  
Stanislav Špaček and Milan Žiaran (Act tool)

Special thanks goes to Jana Komárková for designing the data model, Daniel Tovarňák for consulting the design of the toolset, Vít Šebela for automating the toolset deployment, Vladimír Bouček for implementing the recommender system, Martin Hesko for implementing the visualization for the recommender system, and Michal Čech for integrating it all together.

### References

The developments of the CRUSOE framework resulted in numerous publications. The project summary (corresponsing to release 1.0) was published in Computers & Security journal:
https://www.sciencedirect.com/science/article/pii/S0167404822000086

Release 1.1 with new features and buxfixes was described in the demo paper presented at CNSM 2024 conference:
https://opendl.ifip-tc6.org/db/conf/cnsm/cnsm2024/1571059474.pdf

The list of other related publications can be found at: https://www.muni.cz/en/research/projects/35444

### Acknowledgement

The research and development were supported by the Security Research Programme of the Czech Republic 2015 - 2020 (BV III / 1 VS) granted by the Ministry of the Interior of the Czech Republic under No. VI20172020070 Research of Tools for Cyber Situational Awareness and Decision Support of CSIRT Teams in Protection of Critical Infrastructure.

Further development of the CRUSOE toolset was enabled by the project MSCAfellow5_MUNI (No. CZ.02.01.01/00/22 010/0003229) funded by OP JAK.
