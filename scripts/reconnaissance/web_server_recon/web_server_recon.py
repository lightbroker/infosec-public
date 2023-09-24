import argparse
import subprocess
import json

from ...timestamp import Timestamp


class WebServerReconnaissance:

    def __init__(self, hostname):
        self.hostname = hostname
        self.timestamp = Timestamp().get_current_utc_unix()
        

    def run_command(command):
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            return result.decode('utf-8')
        except subprocess.CalledProcessError as e:
            return f"Error: {e.output.decode('utf-8')}"

    def gather(self):

        # Run Nikto
        nikto_command = f"nikto -h {self.hostname} -output -"
        nikto_output = self.run_command(nikto_command)

        # Run Nmap ssl-enum-ciphers
        nmap_ssl_command = f"nmap --script ssl-enum-ciphers -oX - {self.hostname}"
        nmap_ssl_output = self.run_command(nmap_ssl_command)

        # Run Nmap heartbleed
        nmap_heartbleed_command = f"nmap --script ssl-heartbleed -oX - {self.hostname}"
        nmap_heartbleed_output = self.run_command(nmap_heartbleed_command)

        # Run Nmap http-methods
        nmap_http_methods_command = f"nmap --script http-methods -oX - {self.hostname}"
        nmap_http_methods_output = self.run_command(nmap_http_methods_command)

        # Store the results in a JSON object
        results = {
            "hostname": self.hostname,
            "nikto": nikto_output,
            "nmap_ssl_enum_ciphers": nmap_ssl_output,
            "nmap_heartbleed": nmap_heartbleed_output,
            "nmap_http_methods": nmap_http_methods_output,
            "__metadata": {
                "timestamp": self.timestamp
            }
        }

        # Print the results as JSON
        print(json.dumps(results, indent=4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gather reconnaissance against the web server for a given hostname.")
    parser.add_argument("-t", dest="hostname", help="The target hostname to scan.")
    args = parser.parse_args()

    recon = WebServerReconnaissance(args.hostname)
    recon.gather()
