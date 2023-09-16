'''
    DNS Interrogation Tool

    *** run as sudo

    Usage:
        sudo python ./dns_interrogation.py -h

    Given a supplied hostname:
        1.) discovers authoritative DNS/name servers via `whois`
        2.) determines IP addresses of those servers via `host`
        3.) uses Nmap NSE script dns-brute to automate DNS enumeration, given a provided list 

'''

import argparse
import subprocess
import tldextract


class DnsInterrogation:
    def __init__(self):
        self.results = {
            "authoritative_dns": {
                "ipv4": [],
                "ipv6": [],
            }
        }

    def run(self, hostname, hostlist_filename):
        try:
            print(f'checking whois for {hostname}')
            
            # TODO extract domain
            extract_result = tldextract.extract(hostname)
            tld_plus1 = f'{extract_result.domain}.{extract_result.suffix}'
            print(f'using domain: \"{tld_plus1}\" from hostname: \"{hostname}\"')

            # Run the whois command to get Name Server hostnames
            whois_output = subprocess.check_output(["whois", hostname], universal_newlines=True)
            authoritative_dns = self.results["authoritative_dns"]
            ipv4_list = authoritative_dns["ipv4"]
            ipv6_list = authoritative_dns["ipv6"]

            # Extract and parse Name Server hostnames
            name_servers = []
            for line in whois_output.splitlines():
                if "Name Server:" in line:
                    name_server = line.split(":")[1].strip()
                    print(f'discovered name server: {name_server}')
                    name_servers.append()

            # Run the host command on each Name Server
            for ns in name_servers:
                host_output = subprocess.check_output(["host", ns], universal_newlines=True)

                # Extract and parse IP addresses
                for line in host_output.splitlines():
                    print(f'attempting to extract IP address from line: \"{line}\"')
                    if "has IPv4 address" in line:
                        ipv4_address = line.split()[-1]
                        if ipv4_address not in ipv4_list:
                            ipv4_list.append(ipv4_address)
                    elif "has IPv6 address" in line:
                        ipv6_address = line.split()[-1]
                        if ipv6_address not in ipv6_list:
                            ipv6_list.append(ipv6_address)

            print("Authoritative DNS results:")
            print(self.results)

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
    parser.add_argument("-h", dest="hostlist", help="A list of hosts for Nmap NSE dns-brute (filename)")
    args = parser.parse_args()
    dns_interrogation = DnsInterrogation()
    dns_interrogation.run(args.target, args.hostlist)
