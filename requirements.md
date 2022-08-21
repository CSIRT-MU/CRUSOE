
# Requirements

## 1. Input
 ### - Getting input as IP or domain (via getopt)
 ### - Options:
 - IP: -i/\-\-ip "147.251.147.90"
 - Domain: -d/\-\-domain "fi.muni.cz"
 - Configuration:  -c/\-\-config "PATH"
 
 ### - Input is validated (correct structure of IP or domain name)
 
## 2. Parameters
### -Weight of all attributes are going to be parameterizable with JSON.

### -Weights:

 - Operation system: 
 vendor - default=0.5
 product - default=0.25
 version - default=0.25

- Running software: # split into categories?
 vendor - default=0.5
 product - default=0.25
 version - default=0.25

- Same network service running: 
	service - default=0.5
	port - default=0.25
	protocol - default=0.25



## 3. Similar hosts searching
 ### - Distance based on:
 - Same subnet
 - Same contact 
 - Same organization

### - Distance weights

### - Similarity based on:
- Operation system (from latest scan)
- Running software (antivirus, cms...)
- Running network services
- CVE (cumulative similarity)
- Number of incidents (cumulative similarity)

Risk score is calculated as:

	R = S/D
	where: S = s1 * s2 * s3... / 
		   D = min(d1, d2...)
		   s1..sn are partial similarities
		   d1..dn are distances

## 4. Result printing
