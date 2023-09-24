'''
    DNS Interrogation Tool
    Author: Adam Wilson, https://github.com/lightbroker
    
    *** run as sudo

    Usage:
        sudo python ./dns_interrogation.py -h

    Given a supplied hostname:
        1.) discovers authoritative DNS/name servers via `whois`
        2.) determines IP addresses of those servers via `host`
        3.) uses Nmap NSE script dns-brute to automate DNS enumeration, given a provided list 

'''

import argparse
import calendar
import json
import subprocess
import time
import tldextract

from ip_address_extraction import IpAddressExtraction


class DnsInterrogation:
    def __init__(self):
        self.results = {
            "hostname": None,
            "tld_plus1": None,
            "authoritative_dns": {
                "ipv4": [],
                "ipv6": [],
            }
        }

    def run(self, hostname, hostlist_filename):
        try:
            print(f'checking whois for {hostname}')
            
            self.results["hostname"] = hostname

            # extract eTLD+1
            extract_result = tldextract.extract(hostname)
            tld_plus1 = f'{extract_result.domain}.{extract_result.suffix}'
            self.results["tld_plus1"] = tld_plus1
            print(f'using domain: \"{tld_plus1}\" from hostname: \"{hostname}\"')

            # Run the whois command to get Name Server hostnames
            whois_output = subprocess.check_output(["whois", tld_plus1], universal_newlines=True)
            authoritative_dns = self.results["authoritative_dns"]
            ipv4_list = authoritative_dns["ipv4"]
            ipv6_list = authoritative_dns["ipv6"]

            # Extract and parse Name Server hostnames
            name_servers = []
            for line in whois_output.splitlines():
                if "Name Server:" in line:
                    name_server = line.split(":")[1].strip()
                    print(f'discovered name server: {name_server}')
                    if name_server not in name_servers:
                        name_servers.append(name_server)

            # Run the host command on each Name Server
            for ns in name_servers:
                host_output = subprocess.check_output(["host", ns], universal_newlines=True)

                # Extract and parse IP addresses
                for line in host_output.splitlines():
                    print(f'attempting to extract IP address from line: \"{line}\"')

                    ipv4_address = IpAddressExtraction(line).get_ipv4_address()
                    if ipv4_address is not None:
                        if ipv4_address not in ipv4_list:
                            ipv4_list.append(ipv4_address)

                    ipv6_address = IpAddressExtraction(line).get_ipv6_address()
                    if ipv6_address is not None:
                        if ipv6_address not in ipv6_list:
                            ipv6_list.append(ipv6_address)

            print("Authoritative DNS results:")
            print(self.results)

            timestamp = calendar.timegm(time.gmtime())
            results_filename = f'dns_interrogation.{hostname}.{timestamp}.json'
            with open(results_filename,'w') as f:
                results_json = json.dumps(self.results, indent = 4)
                f.write(results_json)

            # Nmap NSE dns-brute
            nmap_cmd = [
                "nmap",
                "--dns-servers",
                ','.join(ipv4_list),
                "--script",
                "dns-brute",
                "--script-args",
                f"dns-brute.domain={tld_plus1},dns-brute.hostlist={hostlist_filename}",
                "-oX",
                f"nmap.script.dns-brute.{tld_plus1}.xml"
            ]

            dnsbrute_output = subprocess.check_output(nmap_cmd)
            print(dnsbrute_output.decode('utf-8'))

        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DNS Interrogation Tool")
    parser.add_argument("-t", dest="target", help="Target hostname to interrogate")
    parser.add_argument("-l", dest="hostlist", help="A list of hosts for Nmap NSE dns-brute (filename)")
    args = parser.parse_args()
    dns_interrogation = DnsInterrogation()
    dns_interrogation.run(args.target, args.hostlist)
