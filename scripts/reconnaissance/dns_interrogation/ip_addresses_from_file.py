import argparse
from ip_address_extraction import IpAddressExtraction



class IpAddressesFromFile:
    
    def __init__(self) -> None:
        self.results = {
            "ipv4": [],
            "ipv6": []
        }


    def run(self, filename):
        
        ipv4_results = self.results["ipv4"]
        
        with open(filename, 'r') as f:
            lines = f.read().splitlines()

        for l in lines:
            extraction = IpAddressExtraction(l)
            ipv4_matches = extraction.get_all_ipv4()
            for ipv4_match in ipv4_matches:
                if ipv4_match not in ipv4_results:
                    ipv4_results.append(ipv4_match)

        for result in ipv4_results:
            print(result)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='filename', help='Name of file from which to extract IP addresses')
    args = parser.parse_args()
    ips_from_file = IpAddressesFromFile()
    ips_from_file.run(args.filename)
