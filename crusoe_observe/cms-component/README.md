# CMS Component

CMS component is responsible for acquiring information about Content Management Systems runned on webservers.

## Design

Component consist of following items:
1. `scanner/scanner.py` contains code for gathering information about CMS as well as output processing.
2. `data/cms.json` is a configuration file which contains currently discoverable CMS.

## Required packages/versions
At least `Python3.7`.

Required packages are specified in `setup.py` and they will be installed when you use one of the installation methods below.

## Other requirements

WhatWeb plugin is required. Plugin can be found on https://github.com/urbanadventurer/WhatWeb.  
Installation steps are described here https://github.com/urbanadventurer/WhatWeb/wiki/Installation.

You should edit whatweb plugin file <whatweb_path>/plugins/umbraco.rb

into matches insert:

{ :text=>'<script src="https://cdn.muni.cz/DependencyHandler' },


## Usage

### Install

```bash
$ pip install .
```

### Running

```python
>>> from cmsscan.scanner import scanner as cmsscanner

>>> cmsscanner.run('path/to/whatweb',
                   hosts,  # list of webs which will be scanned/or path to the file in case of is_file=True
                   'extra params',  # parameters for whatweb utility
                   'output/path',
                   'cpe/path',  # OPTIONAL, path to the file with information about services which this component detects, default: cms.json
                   logger,  # OPTIONAL, logger instance, by default structlog printlogger
                   is_file)  # OPTIONAL, True if hosts are read from custom file, False otherwise

```
