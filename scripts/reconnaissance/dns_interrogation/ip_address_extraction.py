import re


class IpAddressExtraction:
    def __init__(self, input):
        self.input = input

        patterns = {
            # Source: https://www.geeksforgeeks.org/extract-ip-address-from-file-using-python/
            "ipv4": '(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
            # Source: https://stackoverflow.com/questions/32368008/regular-expression-that-matches-all-valid-format-ipv6-addresses#answer-32368136
            "ipv6": '(?:^|(?<=\s))(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))(?=\s|$)'
        }

        self.ipv4_pattern = re.compile(patterns["ipv4"])
        self.ipv6_pattern = re.compile(patterns["ipv6"])


    def get_ipv4_address(self):
        match = self.ipv4_pattern.search(self.input)
        if match is not None:
            return match[0]


    def get_ipv6_address(self):
        match = self.ipv6_pattern.search(self.input)
        if match is not None:
            return match[0]


    def get_all_ipv4(self):
        match = re.findall(self.ipv4_pattern, self.input)
        if match is not None:
            return match
