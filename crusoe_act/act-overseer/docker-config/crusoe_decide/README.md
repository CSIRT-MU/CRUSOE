# CRUSOE Decide

This package implements functionality for Decision support using attack graphs and Bayesian network.

## Description of analytical process

The main function of the whole analytical process is `analytical_process()` in `process.py`.

The algorithm works as follows:

1. At first find for each mission from the database its configurations using `get_possible_configurations()` method.
2. Then for each mission process its configurations using `process_configuration()` method. To process configuration means
 to mark each component as a "goal" component and according to the goal component:
    1. generate input file for MULVAL
    2. run MULVAL and generate attack graph
    3. extend the graph to bayesian attack graph and infer probability of CIA requirements being affected
    4. apply utility function (which tells how to combine three values CIA into one value)
3. For each configuration take the worst case probability for one of the goal components.
The most resilient configuration is the one with the lowest aforementioned probability.
4. The result of analytical process contains for each mission its most resilient configuration and probability.

Partial results (probabilities of compromise of confidentiality, integrity and availability) 
for each configuration and host in the configuration are stored as nodes and edges 
in the Neo4j database.

## Installation

CRUSOE Decide requires that MULVAL and XSB are installed in the system. First you need to choose where 
MULVAL and XSB will reside (for example in `/opt` directory). Note: Some of the following commands might need sudo on 
your system.

To get MULVAL use these commands:
```bash
$ wget -P /opt https://people.cs.ksu.edu/~xou/argus/software/mulval/mulval_1_1.tar.gz
$ cd /opt
$ tar -xzf mulval_1_1.tar.gz
$ rm mulval_1_1.tar.gz
```

MULVAL also requires XSB:
```bash
$ wget -P /opt http://xsb.sourceforge.net/downloads/XSB.tar.gz
$ tar -xzf XSB.tar.gz
$ rm XSB.tar.gz
```

Set environment variables:
```bash
$ export MULVALROOT=/opt/mulval
$ export XSBROOT=/opt/XSB
$ export PATH=$PATH:$MULVALROOT/bin:$MULVALROOT/utils:$XSBROOT/bin:$XSBROOT/build
```

Before compiling XSB and MULVAL install C++ compiler, Java and bison and flex in you system.
For C++ compiler, bison and flex:
```bash
$ apt-get install build-essential
$ apt-get install bison flex
```

Now you need to make XSB using these commands: 
```bash
$ cd XSB/build
$ ./configure
$ ./makexsb
```

After that you should be able to run XSB with command
```bash
$ /opt/XSB/bin/xsb
```
to exit XSB type `halt.` (with dot at the end).

Now you need to compile MULVAL:
```bash
$ cd /opt/mulval
$ make
```

If output of `make` command contains `javac: Command not found` it means that you don't have java installed in your
system or Java is not in your `PATH`. Note: you need JDK and in it `javac` command. Add to `PATH` the directory which
contains `javac` command.

If you installed Open JDK, you might require also `dom4j` JAR package. Switch to folder for external java packages, 
which has usually form of `/usr/lib/jvm/<name of java>/jre/lib/ext` and then download required JAR using:

```python
wget -P . https://github.com/dom4j/dom4j/releases/download/dom4j_1_6_1/dom4j-1.6.1.jar
```

After successful make of MULVAL you can run testing command (in MULVALROOT directory)
```bash
$ cd testcases/3host/
$ graph_gen.sh input.P -l -p
```

After that you can install CRUSOE Decide using pip from local directory:
```bash
$ pip install . -r requirements.txt
```

These examples install latest commit from `master` branch, for installing a specific tag or a specific branch add `@tag` or `@branch` at the end of URL.

## Set configuration file

Before running the component you need to set variables in `conf.ini` file which can be found in the `example_data` 
folder. 

* Set `mulval_root`/`xsb_root` variables to the same path you used when installing MULVAL / XSB. 
* Variable `mulval_dir` should contain location of directory in which the files necessary for AG generation will be created.
* Variable `interaction_rules_file` points to `crusoe_rules.P` file in the `example_data` folder. Change its value only 
in a case you want to rename this file and rename the file appropriately.

## How to use

Method `analytical_process()` in `process.py` is called when running component. This function accepts password to Neo4j 
database and bolt on which the database runs. 
```python
from crusoe_decide import process
process.analytical_process("neo4j_password", "neo4j_bolt")
```
Logger might be optionally passed as the third argument. The component uses by default `structlog` as logging tool.
Example with logger:
```python
from crusoe_decide import process
process.analytical_process("neo4j_password", "neo4j_bolt", logger=own_logger.get_logger())
```

Please note that your data in the database must be compliant with the CRUSOE data model and all variables 
in conf.ini file should be set correctly. 

## Example output
### Dictionary returned from function:

```python
{'Web mission': {'configuration': {20, 22}, 'probability': (0.2668, 0.0, 0.0)}}
```
The most resilient configuration for `'Web mission'` is configuration `{20, 22}` with probability `0.2668` for 
compromise of confidentiality. Hostnames and IPs for hosts with IDs `{20, 22}` can be easily found in the database.

### Format of results in Neo4j

The component, during the analytical process, computes partial results for each
possible configuration of each mission. The results for a configuration are based 
on the result of configuration's components (i.e. hosts). The results contain, in all cases,
probability of compromise for confidentiality, integrity and availability.

The  appropriate `:Mission` node in the database is connected by the `:HAS` relationship
with a `:Configuration` node. The `:Configuration` node is connected by the 
`:CONTAINS` relationship with its hosts. 
The final path is `(:Mission)-[:HAS]->(:Configuration)-[:CONTAINS]->(:Host)`.
The `(:Configuration)` node contains results (probabilities for confidentiality,
integrity and availability), configuration ID and timestamp of last evaluation.
Results for each host in a configuration are stored on the `:CONTAINS` edge.
