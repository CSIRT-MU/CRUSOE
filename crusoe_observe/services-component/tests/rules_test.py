import pytest
import re

from services_component.core import Result, cpe
from services_component.rules import Rules

test_flows = [
    {"ts": "2018-08-06 09:59:58.577", "te": "2018-08-06 10:04:14.078", "pr": "TCP", "srcip": "147.251.0.1", "srcport:p": "52859", "dstip": "147.251.1.1", "dstport:p": "443", "pkt": "37", "byt": "256", "fl": "1", "hos": "N/A", "hosmaj": "N/A", "hosmin": "N/A", "hosbld": "N/A", "tcpwinsize": "8192", "tcpsynsize": "52", "tcpttl": "125", "hhost": "simple_av", "dnsqname": "", "hurl": ""},
    {"ts": "2018-08-06 09:59:58.577", "te": "2018-08-06 10:04:14.078", "pr": "TCP", "srcip": "147.251.0.2", "srcport:p": "52859", "dstip": "147.251.1.1", "dstport:p": "443", "pkt": "37", "byt": "2048", "fl": "1", "hos": "N/A", "hosmaj": "N/A", "hosmin": "N/A", "hosbld": "N/A", "tcpwinsize": "8192", "tcpsynsize": "52", "tcpttl": "125", "hhost": "cav", "dnsqname": "", "hurl": ""},
    {"ts": "2018-08-06 09:59:58.577", "te": "2018-08-06 10:04:14.078", "pr": "UDP", "srcip": "147.251.0.3", "srcport:p": "52859", "dstip": "147.251.1.1", "dstport:p": "23", "pkt": "37", "byt": "40", "fl": "1", "hos": "N/A", "hosmaj": "N/A", "hosmin": "N/A", "hosbld": "N/A", "tcpwinsize": "8192", "tcpsynsize": "52", "tcpttl": "125", "hhost": "", "dnsqname": "", "hurl": ""},
    {"ts": "2018-08-06 09:59:58.577", "te": "2018-08-06 10:04:14.078", "pr": "TCP", "srcip": "147.251.0.4", "srcport:p": "22", "dstip": "147.251.1.1", "dstport:p": "1024", "pkt": "37", "byt": "53", "fl": "1", "hos": "N/A", "hosmaj": "N/A", "hosmin": "N/A", "hosbld": "N/A", "tcpwinsize": "8192", "tcpsynsize": "52", "tcpttl": "125", "hhost": "", "dnsqname": "", "hurl": ""},
    {"ts": "2018-08-06 09:59:58.577", "te": "2018-08-06 10:04:14.078", "pr": "TCP", "srcip": "147.251.0.5", "srcport:p": "22", "dstip": "147.251.1.1", "dstport:p": "1024", "pkt": "110", "byt": "53", "fl": "1", "hos": "N/A", "hosmaj": "N/A", "hosmin": "N/A", "hosbld": "N/A", "tcpwinsize": "8192", "tcpsynsize": "52", "tcpttl": "125", "hhost": "", "dnsqname": "", "hurl": ""},
    {"ts": "2018-08-06 09:59:58.577", "te": "2018-08-06 10:04:14.078", "pr": "UDP", "srcip": "147.251.0.6", "srcport:p": "1024", "dstip": "147.251.1.1", "dstport:p": "1338", "pkt": "2", "byt": "9999", "fl": "1", "hos": "N/A", "hosmaj": "N/A", "hosmin": "N/A", "hosbld": "N/A", "tcpwinsize": "8192", "tcpsynsize": "52", "tcpttl": "125", "hhost": "top_secret", "dnsqname": "", "hurl": ""},
    {"ts": "2018-08-06 09:59:58.577", "te": "2018-08-06 10:04:14.078", "pr": "UDP", "srcip": "147.251.0.7", "srcport:p": "1024", "dstip": "147.251.1.1", "dstport:p": "1338", "pkt": "2", "byt": "9999", "fl": "1", "hos": "N/A", "hosmaj": "N/A", "hosmin": "N/A", "hosbld": "N/A", "tcpwinsize": "8192", "tcpsynsize": "52", "tcpttl": "125", "hhost": "top_secretx", "dnsqname": "", "hurl": ""},
]

@pytest.fixture
def empty_rules():
    return Rules({})

@pytest.fixture
def simple_rules():
    return Rules({
        "simple_av": {
            "vendor": "simple_antivirus",
            "hostname": "simple_av"
        },
        "complex_av": {
            "vendor": "complex_antivirus",
            "hostname": ["complex_av", "cav"]
        },
        "ssh": {
            "vendor": "ssh_server",
            "srcport": "22"
        },
        "odd_service": {
            "vendor": "odd_client",
            "dstport": "1,3..1024"
        },
        "udp_service": {
            "vendor": "udp_service",
            "protocol": "UDP"
        },
        "256_byte_service": {
            "vendor": "256b_service",
            "bytes": "256"
        },
        "even_packets_service": {
            "vendor": "2k_packet_service",
            "packets": "0,2..65536"
        }
    })

@pytest.fixture
def complex_rules():
    return Rules({
        "specific_service": {
            "vendor": "very_specific_service",
            "product": "very_specific_product",
            "version": "8.1",
            "protocol": "UDP",
            "srcport": "1024",
            "dstport": ["1337", "1338"],
            "hostname": ["top_secret", "do_not_look"],
            "bytes": "9999",
            "packets": "2"
        },
        "unspecific_service": {
            "vendor": "very_unspecific_service",
            "protocol": ["TCP", "UDP", "ICMP"],
            "srcport": "0,2..65536",
            "dstport": "0,3..65536",
            "hostname": "x",
            "bytes": "0..16384"
        }
    })

### Constructor
def test_empty_rules(empty_rules):
    assert empty_rules.rules == {}

def test_simple_rules(simple_rules):
    assert simple_rules.rules == {
        "simple_av": {
            "vendor": "simple_antivirus",
            "product": None,
            "version": None,
            "hostname": [re.compile("simple_av")],
        },
        "complex_av": {
            "vendor": "complex_antivirus",
            "product": None,
            "version": None,
            "hostname": [re.compile("complex_av"), re.compile("cav")],
        },
        "ssh": {
            "vendor": "ssh_server",
            "product": None,
            "version": None,
            "srcport": range(22,23),
        },
        "odd_service": {
            "vendor": "odd_client",
            "product": None,
            "version": None,
            "dstport": range(1, 1024, 2),
        },
        "udp_service": {
            "vendor": "udp_service",
            "product": None,
            "version": None,
            "protocol": ["UDP"],
        },
        "256_byte_service": {
            "vendor": "256b_service",
            "product": None,
            "version": None,
            "bytes": range(256, 257),
        },
        "even_packets_service": {
            "vendor": "2k_packet_service",
            "product": None,
            "version": None,
            "packets": range(0, 65536, 2),
        }
    }

def test_complex_rules(complex_rules):
    assert complex_rules.rules == {
        "specific_service": {
            "vendor": "very_specific_service",
            "product": "very_specific_product",
            "version": "8.1",
            "protocol": ["UDP"],
            "srcport": range(1024, 1025),
            "dstport": [1337, 1338],
            "hostname": [re.compile("top_secret"), re.compile("do_not_look")],
            "bytes": range(9999, 10000),
            "packets": range(2, 3)
        },
        "unspecific_service": {
            "vendor": "very_unspecific_service",
            "product": None,
            "version": None,
            "protocol": ["TCP", "UDP", "ICMP"],
            "srcport": range(0, 65536, 2),
            "dstport": range(0, 65536, 3),
            "hostname": [re.compile("x")],
            "bytes": range(0, 16384)
        }
    }

### Match_hostname method
def test_match_hostname():
    assert not Rules.match_hostname(test_flows[1], [re.compile("simple_av")])
    assert Rules.match_hostname(test_flows[1], [re.compile("complex_av"), re.compile("cav")])

### Match_port method
def test_match_port():
    assert not Rules.match_port(80, range(1, 50))
    assert Rules.match_port(80, range(1, 100))
    assert not Rules.match_port(0, [1, 2, 3, 4])
    assert Rules.match_port(0, [1, 2, 0, 3, 4])
    assert not Rules.match_port(21, range(0, 30, 2))
    assert Rules.match_port(21, range(0, 30, 3))

### Match_protocol method
def test_match_protocol():
    assert not Rules.match_protocol("TCP", ["UDP"])
    assert Rules.match_protocol("TCP", ["TCP"])
    assert Rules.match_protocol("ICMP", ["TCP", "UDP", "ICMP"])

### Match_bytes method
def test_match_bytes():
    assert not Rules.match_bytes(80, range(1, 50))
    assert Rules.match_bytes(80, range(1, 100))
    assert not Rules.match_bytes(0, [1, 2, 3, 4])
    assert Rules.match_bytes(0, [1, 2, 0, 3, 4])
    assert not Rules.match_bytes(21, range(0, 30, 2))
    assert Rules.match_bytes(21, range(0, 30, 3))


### Match_packets method
def test_match_packets():
    assert not Rules.match_packets(80, range(1, 50))
    assert Rules.match_packets(80, range(1, 100))
    assert not Rules.match_packets(0, [1, 2, 3, 4])
    assert Rules.match_packets(0, [1, 2, 0, 3, 4])
    assert not Rules.match_packets(21, range(0, 30, 2))
    assert Rules.match_packets(21, range(0, 30, 3))

### Match method
def test_match_empty(empty_rules):
    assert empty_rules.match(test_flows).count() == 0

def test_match_simple(simple_rules):
    f = lambda y: set(map(lambda x: cpe(*x[1]), matched[y].all()))
    matched = simple_rules.match(test_flows)
    assert set(["256b_service:*:*", "odd_client:*:*", "simple_antivirus:*:*"]) == f("147.251.0.1")
    assert set(["complex_antivirus:*:*", "odd_client:*:*"]) == f("147.251.0.2")
    assert set(["udp_service:*:*", "odd_client:*:*"]) == f("147.251.0.3")
    assert set(["ssh_server:*:*"]) == f("147.251.0.4")
    assert set(["2k_packet_service:*:*", "ssh_server:*:*"]) == f("147.251.0.5")

def test_match_complex(complex_rules):
    matched = complex_rules.match(test_flows)
    assert matched["147.251.0.6"].total() == 1
    assert matched["147.251.0.6"]["very_specific_service"]["very_specific_product"]["8.1"].current() == 1
    assert matched["147.251.0.7"].total() == 2
    assert matched["147.251.0.7"]["very_specific_service"]["very_specific_product"]["8.1"].current() == 1
    assert matched["147.251.0.7"]["very_unspecific_service"].current() == 1
