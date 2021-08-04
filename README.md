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

### Authors

The authors of the CRUSOE toolset are:

Martin Laštovička, Jakub Bartoloměj Košuth, Danei Filakovský, and Martin Husák (Observe tool)  
Lukáš Matta and Martin Husák (Orient tool)  
Lukáš Sadlek, Michal Javorník, and Martin Husák (Decide tool)  
Stanislav Špaček and Milan Žiaran (Act tool)

Special thanks goes to Jana Komárková for designing the data model and Daniel Tovarňák for consulting the design of the toolset.

### References

The developments of the CRUSOE framework resulted in numerous publications. Their list can be found at: https://www.muni.cz/en/research/projects/35444

### Acknowledgement

The research and development were supported by the Security Research Programme of the Czech Republic 2015 - 2020 (BV III / 1 VS) granted by the Ministry of the Interior of the Czech Republic under No. VI20172020070 Research of Tools for Cyber Situational Awareness and Decision Support of CSIRT Teams in Protection of Critical Infrastructure.
