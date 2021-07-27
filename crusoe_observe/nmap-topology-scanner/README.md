# Nmap Topology Scanner

Nmap Topology Scanner is component responsible for mapping the topology of network.  
It uses nmap to  traceroute whole IP ranges, saves these data to JSON files, which are then parsed and saved to Neo4j database.

## Design
Nmap Topology scanner consist of one file:
1. `scanner.py` contains methods which are able to scan network IP ranges and parse output to desired format.

## Required packages/versions
At least `Python3.7`.

Required packages are specified in `setup.py` and they will be installed when you use one of the installation methods below.

Nmap needs to be installed on the system. (`sudo apt install nmap`)

## Usage

### Install

```bash
$ pip install .
```

### Running

```python
>>> from nmap_topology_scanner.scanner import scan, topology_scan

# Preparation of subnets 147.251.X.0/24 where X is anything else without FI (42-54, 58, 106)
>>> indexes = list(range(42)) + list(range(55, 58)) + list(range(59, 106)) + list(range(107, 256))
>>> subnets = [f"147.251.{x}.0/24" for x in indexes]

# vertical scan
>>> scan(subnets, 'nmap args', logger instance)  # if no logger instance is specified, default printlogger of structlog will be used
# Example
>>> scan(subnets, '-sV -n --top-ports 1500') 

# topology scan
>>> scan(subnets, logger instance)  # if no logger instance is specified, default printlogger of structlog will be used
```

## Other information

### Approximate time for scan

all results are from MU subnet (147.251.0.0/16 excluding FI range) => 240 times '/24' subnets

| Nmap mode | Duration(hh:mm) | Services | IP addrs | services per IP | Start | End | Day
| --------- | --------- | --------- | --------- | --------- | --------- | --------- |  --------- |
-sV -n -F -T5 | 8:05 | 8380 | 6819 | 1.229 | 15-04 9:07 | 15-04 17:12 | Monday |
-sV -n -F -T4 | 8:40 | 8091 | 5527 | 1.464 | 22-03 8:45 | 22-03 17:25 | Friday |
-sV -n -T5 | 16:10 | 11344 | 5771 | 1.966 | 18-03 7:57 | 19-03 00:07 | Tuesday |
-sV -n -T4 | 39:22 | 13247 | 5123 | 2.586 | 16-04 8:08 | 17-04 23:30 | Tuesday, Wednesday |
-sV -n | 88:24 | 12757 | 4826 | 2.643 | 23-04 09:00 | 27-04 01:24 | Tuesday - Saturday |
-sV -n -T4 (single run) | ??? | ??? | ??? | ??? | ??? | ??? |

### Sample output
```
# topology scan
{
  "src_ip": "2001:718:801:384::101f",
  "data": [
    {
      "dst_ip": "147.251.14.46",
      "proto": "icmp",
      "hops": [
        {
          "ttl": "1",
          "ip": "147.251.55.1",
          "rtt": "13.05"
        },
        {
          "ttl": "2",
          "ip": "147.251.19.225",
          "rtt": "14.36"
        },
        {
          "ttl": "3",
          "ip": "147.251.244.25",
          "rtt": "20.92"
        },
        {
          "ttl": "4",
          "ip": "147.251.241.178",
          "rtt": "17.25"
        },
        {
          "ttl": "5",
          "ip": "147.251.14.46",
          "rtt": "14.37"
        }
      ]
    }
  ],
  "time": "TODO"
}


# vertical scan
{
  "src_ip": "147.251.13.92",
  "data": {
    "147.251.14.46": {
      "nmap": {
        "command_line": "nmap -oX - -sV 147.251.14.46",
        "scaninfo": {
          "tcp": {
            "method": "connect",
            "services": "1,3-4,6-7, ... "
          }
        },
        "scanstats": {
          "timestr": "Tue Apr 30 12:05:42 2019",
          "elapsed": "16.68",
          "uphosts": "1",
          "downhosts": "0",
          "totalhosts": "1"
        }
      },
      "scan": {
        "147.251.14.46": {
          "hostnames": [
            {
              "name": "crusoe.ics.muni.cz",
              "type": "PTR"
            }
          ],
          "addresses": {
            "ipv4": "147.251.14.46"
          },
          "vendor": {},
          "status": {
            "state": "up",
            "reason": "syn-ack"
          },
          "tcp": {
            "22": {
              "state": "open",
              "reason": "syn-ack",
              "name": "ssh",
              "product": "OpenSSH",
              "version": "6.7p1 Debian 5+deb8u7",
              "extrainfo": "protocol 2.0",
              "conf": "10",
              "cpe": "cpe:/o:linux:linux_kernel"
            },
            "80": {
              "state": "open",
              "reason": "syn-ack",
              "name": "http",
              "product": "Apache httpd",
              "version": "2.4.10",
              "extrainfo": "",
              "conf": "10",
              "cpe": "cpe:/a:apache:http_server:2.4.10"
            },
            "111": {
              "state": "open",
              "reason": "syn-ack",
              "name": "rpcbind",
              "product": "",
              "version": "2-4",
              "extrainfo": "RPC #100000",
              "conf": "10",
              "cpe": ""
            },
            "443": {
              "state": "open",
              "reason": "syn-ack",
              "name": "http",
              "product": "Apache httpd",
              "version": "2.4.10",
              "extrainfo": "(Debian)",
              "conf": "10",
              "cpe": "cpe:/a:apache:http_server:2.4.10"
            },
            "5555": {
              "state": "open",
              "reason": "syn-ack",
              "name": "http",
              "product": "Tornado httpd",
              "version": "5.0.2",
              "extrainfo": "",
              "conf": "10",
              "cpe": "cpe:/a:tornadoweb:tornado:5.0.2"
            }
          }
        }
      }
    }
  }
}
```
