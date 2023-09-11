import argparse
import subprocess

class DnsInterrogation:
    def __init__(self):
        self.results = {
            "IPv4": [],
            "IPv6": [],
        }

    def with_hostname(self, hostname):
        try:
            print(f'checking whois for {hostname}')
            
            # Run the whois command to get Name Server hostnames
            whois_output = subprocess.check_output(["whois", hostname], universal_newlines=True)

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
                    if "has IPv4 address" in line:
                        ipv4_address = line.split()[-1]
                        print(f'discovered IPv4 address: {ipv4_address}')
                        self.results["IPv4"].append(ipv4_address)
                    elif "has IPv6 address" in line:
                        ipv6_address = line.split()[-1]
                        print(f'discovered IPv6 address: {ipv6_address}')
                        self.results["IPv6"].append(ipv6_address)

            print("Results:")
            print(self.results)

        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DNS Interrogation Tool")
    parser.add_argument("-t", dest="target", help="Target hostname to interrogate")
    args = parser.parse_args()
    dns_interrogation = DnsInterrogation()
    dns_interrogation.with_hostname(args.target)
