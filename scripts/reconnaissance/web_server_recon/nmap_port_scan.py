import argparse
import calendar
import subprocess
import time


class NmapPortScan:

    def __init__(self, ip_address) -> None:
        self.ip_address = ip_address


    def run(self):
        ts = calendar.timegm(time.gmtime())
        print(ts)
        try:
            cmd = ['nmap', '-sT', self.ip_address, '-p-', '-oX', f'nmap.-sT.-p-.{self.ip_address}.{ts}.xml']
            nmap_outbytes = subprocess.check_output(cmd)
            nmap_output = nmap_outbytes.decode('utf-8')
            print(nmap_output)
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='ipv4_address', help='Target IPv4 address')
    args = parser.parse_args()
    nmap_scan = NmapPortScan(args.ipv4_address)
    nmap_scan.run()
