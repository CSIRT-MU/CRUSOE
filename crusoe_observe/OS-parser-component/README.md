# OS-parser
OS parser is CRUSOE component developed for identification of OS from network flows using various methods.

## Design
Component consists of following parts:

1. Directory `data` consists of configuration/data files that are used in OS identification process. 
2. Directory `method` contains implementation of discovery methods: Specific domains, TCP/IP parameters, user-Agent.
3. `OS_parser.py` is used for flow parsing as well as aggregation of results.
4. `run.py` serves as an entry point of the component.

## Required packages/versions
At least `Python3.6`.

Required packages are specified in `setup.py` and they will be installed when you use one of the installation methods below.

TCP/IP method expects ML model or dataset for correct functionality. You can either use default `data/train.csv` dataset or use your own model/dataset. 
You need to specify path to the dataset in config file (Default path is `/usr/share/crusoe/os_dataset.csv`) or path to the ML model (Default path is `/var/tmp/crusoe/os_model.pkl`).
One of the above options (datased/model) is sufficient.
## Usage

### Install

```bash
$ pip install .
```

### Running

```python
>>> from osrest import run

>>> run.parse('input/flow_path', 'output_path')

'2020-06-29 15:31.47 OS detection is starting
2020-06-29 15:31.50 parsed flows: 672137
2020-06-29 15:31.50 Method start                   method=useragent
2020-06-29 15:31.50 Method finish                  method=useragent
2020-06-29 15:31.50 Method start                   method=domain
2020-06-29 15:32.01 Method finish                  method=domain
2020-06-29 15:32.01 Method start                   method=tcpml
2020-06-29 15:32.05 Method finish                  method=tcpml
2020-06-29 15:32.05 2020-06-29 15:30:00 done
New: 9707, unchanged: 0, changed: 0, inactive: 0 sessions'

```
