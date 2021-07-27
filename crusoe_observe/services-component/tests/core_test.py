import pytest

from math import isclose
from services_component.core import *
from copy import deepcopy

### Free functions

def test_cpe():
    assert cpe("abc", None, "g3h", "123.5", None) == "abc:*:g3h:123.5:*"

def test_cpe_vendor():
    assert cpe_vendor() == "*"
    assert cpe_vendor("abcDeF3") == "abcDeF3"

def test_cpe_product():
    assert cpe_product() == "*:*"
    assert cpe_product("abcDeF3") == "abcDeF3:*"
    assert cpe_product("abcDeF3", "XyZ") == "abcDeF3:XyZ"

def test_cpe_version():
    assert cpe_version() == "*:*:*"
    assert cpe_version("abcDeF3") == "abcDeF3:*:*"
    assert cpe_version("abcDeF3", "XyZ") == "abcDeF3:XyZ:*"
    assert cpe_version("abcDeF3", "XyZ", 3.14) == "abcDeF3:XyZ:3.14"

### Version
@pytest.fixture
def version0():
    return Version("0.1")

@pytest.fixture
def version1():
    v = Version("1.0")
    v.counter = 123
    return v

@pytest.fixture
def version2():
    v = Version("1.5")
    v.counter = 3
    return v

@pytest.fixture
def version3():
    v = Version("2.0.1")
    v.counter = 21
    return v

@pytest.fixture
def version4():
    v = Version("0.99")
    v.counter = 10
    return v

@pytest.fixture
def version5():
    v = Version("1.0")
    v.counter = 5
    return v

### Version constructor
def test_version_init(version0):
    assert version0.name == "0.1"
    assert version0.counter == 0

### Version str
def test_version_str(version0, version1):
    assert str(version0) == "0.1"
    assert str(version1) == "1.0"

### Version inc
def test_version_inc(version0):
    version0.inc()
    assert version0.counter == 1
    version0.inc(123)
    assert version0.counter == 124

### Version total
def test_version_total(version0, version1):
    assert version0.total() == 0
    assert version1.total() == 123

### Version most
def test_version_most(version0, version1):
    assert version0.most() == (0, [None])
    assert version1.most() == (123, ["1.0"])

### Version merge
def test_version_merge(version0, version1):
    version0.counter = 50
    version0.merge(version1)
    assert version0.counter == 50 + 123
    version0.merge(version0)
    assert version0.counter == (50 + 123) * 2

def test_version_merge_weight(version0, version1):
    version0.counter = 50
    version0.merge(version1, 5)
    assert version0.counter == 50 + 123 * 5
    version0.merge(version0, 3)
    assert version0.counter == (50 + 123 * 5) * 4

### Version normalize
def test_version_normalize(version0, version1):
    version0.normalize()
    assert isclose(version0.counter, 0.0)
    version1.normalize()
    assert isclose(version1.counter, 1.0)

def test_version_normalize_total(version0, version1):
    version0.normalize(2)
    assert isclose(version0.counter, 0.0)
    version1.normalize(2)
    assert isclose(version1.counter, 123/2)

### Version all
def test_version_all(version0, version1):
    assert version0.all() == []
    assert version1.all() == [(123, ["1.0"])]

### Product
@pytest.fixture
def product0():
    return Product("product")

@pytest.fixture
def product1(version0, version1, version2):
    p = Product("cool_product")
    p.counter = 5
    for item in (version0, version1, version2):
        p.items[item.name] = deepcopy(item)
    return p

@pytest.fixture
def product2(version3, version4, version5):
    p = Product("boring_product")
    p.counter = 3
    for item in (version3, version4, version5):
        p.items[item.name] = deepcopy(item)
    return p

@pytest.fixture
def product3(version1, version2, version3, version4):
    p = Product("mediocre_product")
    for item in (version1, version2, version3, version4):
        p.items[item.name] = deepcopy(item)
    return p

@pytest.fixture
def product4(version1, version4):
    p = Product("clueless_product")
    for item in (version1, version4):
        p.items[item.name] = deepcopy(item)
    return p

@pytest.fixture
def product5(version1):
    p = Product("creative_product")
    for item in (version1,):
        p.items[item.name] = deepcopy(item)
    return p

@pytest.fixture
def product6():
    p = Product("void_product")
    p.counter = 7
    return p

### Product constructor
def test_product_init(product0):
    assert product0.name == "product"
    assert product0.counter == 0

### Product str
def test_product_str(product0, product1):
    assert str(product0) == "product"
    assert str(product1) == "cool_product"

### Product inc
def test_product_inc(product0):
    product0.inc()
    assert product0.counter == 1
    product0.inc(123)
    assert product0.counter == 124

### Product total
def test_product_total(product0, product1):
    assert product0.total() == 0
    assert product1.total() == 131

### Product most
def test_product_most(product0, product1):
    assert product0.most() == (0, [None, None])
    assert product1.most() == (128, ["cool_product", "1.0"])

### Product merge
def test_product_merge(product1, product4):
    p1t = product1.total()
    p1c = product1.counter
    p4t = product4.total()
    p4c = product4.counter
    product1.merge(product4)
    assert product1.counter == p1c + p4c
    assert product1.total() == p1t + p4t
    product1.merge(product1)
    assert product1.counter == 2 * (p1c + p4c)
    assert product1.total() == 2 * (p1t + p4t)

def test_product_merge_weight(product1, product4):
    p1t = product1.total()
    p1c = product1.counter
    p4t = product4.total()
    p4c = product4.counter
    product1.merge(product4, 3)
    assert product1.counter == p1c + 3 * p4c
    assert product1.total() == p1t + 3 * p4t
    product1.merge(product1, 3)
    assert product1.counter == 4 * (p1c + 3 * p4c)
    assert product1.total() == 4 * (p1t + 3 * p4t)

### Product normalize
def test_product_normalize(product0, product1):
    product0.normalize()
    assert isclose(product0.total(), 0.0)
    product1.normalize()
    assert isclose(product1.total(), 1.0)

def test_product_normalize_total(product0, product1):
    product0.normalize(2)
    assert isclose(product0.total(), 0.0)
    p1t = product1.total()
    product1.normalize(2)
    assert isclose(product1.total(), p1t / 2)

### Product all
def test_product_all(product0, product1, product6):
    assert product0.all() == []
    assert product1.all() == [(128, ["cool_product", "1.0"]), (8, ["cool_product", "1.5"])]
    assert product6.all() == [(7, ["void_product", None])]

### Vendor
@pytest.fixture
def vendor0():
    return Vendor("vendor")

@pytest.fixture
def vendor1(product0, product1, product2):
    v = Vendor("cool_vendor")
    v.counter = 5
    for item in (product0, product1, product2):
        v.items[item.name] = deepcopy(item)
    return v

@pytest.fixture
def vendor2(product3, product4, product5):
    v = Vendor("boring_product")
    v.counter = 3
    for item in (product3, product4, product5):
        v.items[item.name] = deepcopy(item)
    return v

@pytest.fixture
def vendor3(product1, product2, product3, product4):
    v = Vendor("mediocre_vendor")
    for item in (product1, product2, product3, product4):
        v.items[item.name] = deepcopy(item)
    return v

@pytest.fixture
def vendor4(product1, product4):
    v = Vendor("clueless_vendor")
    for item in (product1, product4):
        v.items[item.name] = deepcopy(item)
    return v

@pytest.fixture
def vendor5(product1):
    v = Vendor("creative_vendor")
    for item in (product1,):
        v.items[item.name] = deepcopy(item)
    return v

@pytest.fixture
def vendor6():
    v = Vendor("void_vendor")
    v.counter = 7
    return v

### Vendor constructor
def test_vendor_init(vendor0):
    assert vendor0.name == "vendor"
    assert vendor0.counter == 0

### Vendor str
def test_vendor_str(vendor0, vendor1):
    assert str(vendor0) == "vendor"
    assert str(vendor1) == "cool_vendor"

### Vendor inc
def test_vendor_inc(vendor0):
    vendor0.inc()
    assert vendor0.counter == 1
    vendor0.inc(123)
    assert vendor0.counter == 124

### Vendor total
def test_vendor_total(vendor0, vendor1):
    assert vendor0.total() == 0
    assert vendor1.total() == 175

### Vendor most
def test_vendor_most(vendor0, vendor1):
    assert vendor0.most() == (0, [None, None, None])
    assert vendor1.most() == (133, ["cool_vendor", "cool_product", "1.0"])

### Vendor merge
def test_vendor_merge(vendor1, vendor4):
    v1t = vendor1.total()
    v1c = vendor1.counter
    v4t = vendor4.total()
    v4c = vendor4.counter
    vendor1.merge(vendor4)
    assert vendor1.counter == v1c + v4c
    assert vendor1.total() == v1t + v4t
    vendor1.merge(vendor1)
    assert vendor1.counter == 2 * (v1c + v4c)
    assert vendor1.total() == 2 * (v1t + v4t)

def test_vendor_merge_weight(vendor1, vendor4):
    v1t = vendor1.total()
    v1c = vendor1.counter
    v4t = vendor4.total()
    v4c = vendor4.counter
    vendor1.merge(vendor4, 3)
    assert vendor1.counter == v1c + 3 * v4c
    assert vendor1.total() == v1t + 3 * v4t
    vendor1.merge(vendor1, 3)
    assert vendor1.counter == 4 * (v1c + 3 * v4c)
    assert vendor1.total() == 4 * (v1t + 3 * v4t)

### Vendor normalize
def test_vendor_normalize(vendor0, vendor1):
    vendor0.normalize()
    assert isclose(vendor0.total(), 0.0)
    vendor1.normalize()
    assert isclose(vendor1.total(), 1.0)

def test_vendor_normalize_total(vendor0, vendor1):
    vendor0.normalize(2)
    assert isclose(vendor0.total(), 0.0)
    p1t = vendor1.total()
    vendor1.normalize(2)
    assert isclose(vendor1.total(), p1t / 2)

### Vendor all
def test_vendor_all(vendor0, vendor1, vendor6):
    assert vendor0.all() == []
    assert vendor1.all() == [
        (133, ['cool_vendor', 'cool_product', '1.0']),
        (13, ['cool_vendor', 'cool_product', '1.5']),
        (29, ['cool_vendor', 'boring_product', '2.0.1']),
        (18, ['cool_vendor', 'boring_product', '0.99']),
        (13, ['cool_vendor', 'boring_product', '1.0']),
    ]
    assert vendor6.all() == [(7, ["void_vendor", None, None])]

### Hierarchy
@pytest.fixture
def hierarchy0():
    return Hierarchy()

@pytest.fixture
def hierarchy1(vendor0, vendor1, vendor2):
    h = Hierarchy()
    h.counter = 5
    for item in (vendor0, vendor1, vendor2):
        h.items[item.name] = deepcopy(item)
    return h

@pytest.fixture
def hierarchy2(vendor3, vendor4, vendor5):
    h = Hierarchy()
    h.counter = 3
    for item in (vendor3, vendor4, vendor5):
        h.items[item.name] = deepcopy(item)
    return h

@pytest.fixture
def hierarchy3(vendor1, vendor2, vendor3, vendor4):
    h = Hierarchy()
    for item in (vendor1, vendor2, vendor3, vendor4):
        h.items[item.name] = deepcopy(item)
    return h

@pytest.fixture
def hierarchy4(vendor1, vendor4):
    h = Hierarchy()
    for item in (vendor1, vendor4):
        h.items[item.name] = deepcopy(item)
    return h

@pytest.fixture
def hierarchy5(vendor1):
    h = Hierarchy()
    for item in (vendor1,):
        h.items[item.name] = deepcopy(item)
    return h

@pytest.fixture
def hierarchy6():
    h = Hierarchy()
    h.counter = 7
    return h

### Hierarchy constructor
def test_hierarchy_init(hierarchy0):
    assert hierarchy0.counter == 0

### Hierarchy inc
def test_hierarchy_inc(hierarchy0):
    hierarchy0.inc()
    assert hierarchy0.counter == 1
    hierarchy0.inc(123)
    assert hierarchy0.counter == 124

### Hierarchy total
def test_hierarchy_total(hierarchy0, hierarchy1):
    assert hierarchy0.total() == 0
    assert hierarchy1.total() == 596

### Hierarchy most
def test_hierarchy_most(hierarchy0, hierarchy1):
    assert hierarchy0.most() == (0, [None, None, None])
    assert hierarchy1.most() == (138, ["cool_vendor", "cool_product", "1.0"])

### Hierarchy merge
def test_hierarchy_merge(hierarchy1, hierarchy4):
    h1t = hierarchy1.total()
    h1c = hierarchy1.counter
    h4t = hierarchy4.total()
    h4c = hierarchy4.counter
    hierarchy1.merge(hierarchy4)
    assert hierarchy1.counter == h1c + h4c
    assert hierarchy1.total() == h1t + h4t
    hierarchy1.merge(hierarchy1)
    assert hierarchy1.counter == 2 * (h1c + h4c)
    assert hierarchy1.total() == 2 * (h1t + h4t)

def test_hierarchy_merge_weight(hierarchy1, hierarchy4):
    v1t = hierarchy1.total()
    v1c = hierarchy1.counter
    v4t = hierarchy4.total()
    v4c = hierarchy4.counter
    hierarchy1.merge(hierarchy4, 3)
    assert hierarchy1.counter == v1c + 3 * v4c
    assert hierarchy1.total() == v1t + 3 * v4t
    hierarchy1.merge(hierarchy1, 3)
    assert hierarchy1.counter == 4 * (v1c + 3 * v4c)
    assert hierarchy1.total() == 4 * (v1t + 3 * v4t)

### Hierarchy normalize
def test_hierarchy_normalize(hierarchy0, hierarchy1):
    hierarchy0.normalize()
    assert isclose(hierarchy0.total(), 0.0)
    hierarchy1.normalize()
    assert isclose(hierarchy1.total(), 1.0)

def test_hierarchy_normalize_total(hierarchy0, hierarchy1):
    hierarchy0.normalize(2)
    assert isclose(hierarchy0.total(), 0.0)
    h1t = hierarchy1.total()
    hierarchy1.normalize(2)
    assert isclose(hierarchy1.total(), h1t / 2)

### Vendor all
def test_hierarchy_all(hierarchy0, hierarchy1, hierarchy6):
    assert hierarchy0.all() == []
    assert hierarchy1.all() == [
        (138, ['cool_vendor', 'cool_product', '1.0']),
        (18, ['cool_vendor', 'cool_product', '1.5']),
        (34, ['cool_vendor', 'boring_product', '2.0.1']),
        (23, ['cool_vendor', 'boring_product', '0.99']),
        (18, ['cool_vendor', 'boring_product', '1.0']),
        (131, ['boring_product', 'mediocre_product', '1.0']),
        (11, ['boring_product', 'mediocre_product', '1.5']),
        (29, ['boring_product', 'mediocre_product', '2.0.1']),
        (18, ['boring_product', 'mediocre_product', '0.99']),
        (131, ['boring_product', 'clueless_product', '1.0']),
        (18, ['boring_product', 'clueless_product', '0.99']),
        (131, ['boring_product', 'creative_product', '1.0']),
    ]
    assert hierarchy6.all() == [(7, [None, None, None])]

### Result
@pytest.fixture
def result0():
    return Result()

@pytest.fixture
def result1(hierarchy0, hierarchy1, hierarchy2):
    r = Result()
    r.items["127.0.0.1"] = deepcopy(hierarchy0)
    r.items["127.0.0.2"] = deepcopy(hierarchy1)
    r.items["127.0.0.3"] = deepcopy(hierarchy2)
    return r

@pytest.fixture
def result2(hierarchy3, hierarchy4, hierarchy5):
    r = Result()
    r.items["127.0.0.4"] = deepcopy(hierarchy3)
    r.items["127.0.0.5"] = deepcopy(hierarchy4)
    r.items["127.0.0.6"] = deepcopy(hierarchy5)
    return r

@pytest.fixture
def result3(hierarchy1, hierarchy2, hierarchy3, hierarchy4):
    r = Result()
    r.items["127.0.0.2"] = deepcopy(hierarchy1)
    r.items["127.0.0.3"] = deepcopy(hierarchy2)
    r.items["127.0.0.4"] = deepcopy(hierarchy3)
    r.items["127.0.0.5"] = deepcopy(hierarchy4)
    return r

@pytest.fixture
def result4(hierarchy1, hierarchy4):
    r = Result()
    r.items["127.0.0.2"] = deepcopy(hierarchy1)
    r.items["127.0.0.5"] = deepcopy(hierarchy4)
    return r

@pytest.fixture
def result5(hierarchy1):
    r = Result()
    r.items["127.0.0.2"] = deepcopy(hierarchy1)
    return r

### Result constructor
def test_result_init(result0):
    assert result0.items == {}

### Result merge
def test_result_merge(result1, result4):
    t = lambda y: sum(map(lambda x: x.total(), y.items.values()))
    r1t = t(result1)
    r4t = t(result4)
    result1.merge(result4)
    assert t(result1) == r1t + r4t
    result1.merge(result1)
    assert t(result1) == 2 * (r1t + r4t)

def test_result_merge_weight(result1, result4):
    t = lambda y: sum(map(lambda x: x.total(), y.items.values()))
    r1t = t(result1)
    r4t = t(result4)
    result1.merge(result4, 3)
    assert t(result1) == r1t + 3 * r4t
    result1.merge(result1, 3)
    assert t(result1) == 4 * (r1t + 3 * r4t)

### Result normalize
def test_result_normalize(result0, result1):
    t = lambda y: sum(map(lambda x: x.total(), y.items.values()))
    result0.normalize()
    assert isclose(t(result0), 0.0)
    result1.normalize()
    assert isclose(t(result1), 2.0)

### Result finalize
def test_result_finalize(result0, result1):
    assert result0.finalize("category") == []
    assert result1.finalize("category") == [
        {
            "ip": "127.0.0.1",
            "vendor": None,
            "product": None,
            "type": "category",
            "name": "*:*",
            "version": "*:*:*",
        },
        {
            "ip": "127.0.0.2",
            "vendor": "cool_vendor",
            "product": "cool_product",
            "type": "category",
            "name": "cool_vendor:cool_product",
            "version": "cool_vendor:cool_product:1.0",
        },
        {
            "ip": "127.0.0.3",
            "vendor": "mediocre_vendor",
            "product": "cool_product",
            "type": "category",
            "name": "mediocre_vendor:cool_product",
            "version": "mediocre_vendor:cool_product:1.0",
        },
    ]
