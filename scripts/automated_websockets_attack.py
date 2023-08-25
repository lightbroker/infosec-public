'''
  Usage:
  $ python ./automated_websockets_attack.py -h
'''

import argparse
import json
import websocket


class AutomatedWebSocketsAttack:

    def __init__(self, access_token_file, payloads_file, template_file):
        # get access token
        with open(access_token_file, 'r') as f:
            self.access_token = f.read()

        # get payloads list
        with open(payloads_file, 'r') as f:
            payloads = f.read().splitlines()

        # get JSON template (based on a legit request captured)
        with open(template_file, 'r') as f:
            contents = f.read()
            self.template = json.loads(contents)

        self.custom_payloads = []
        for payload in payloads:
            # replace token placeholders with attack payloads
            custom_payload = str(self.template).replace('$$$', payload)
            self.custom_payloads.append(custom_payload)

        self.ws_target_url = 'wss://host/?key=value'
        self.origin = 'https://origin/',
        self.host = 'host'


    def run(self):
        websocket.enableTrace(True)

        for payload in self.custom_payloads:
            ws = websocket.WebSocket()
            ws.connect(url=self.ws_target_url, origin=self.origin, host=self.host, headers={ 'Cookie: key=value' })
            message = f'{payload}'
            ws.send(message.encode())
            result = ws.recv()
            print(f'{result}')
            ws.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Set up and fire a series of requests against WebSockets resources')
    parser.add_argument('-a', dest='access_token_file', required=True, help='JWT/JWS access token (name of file containing token value)')
    parser.add_argument('-p', dest='payloads_file', required=True, help='list of payloads (name of file containing payloads)')
    parser.add_argument('-t', dest='template_file', required=True, help='request template (name of JSON file)')

    args = parser.parse_args()

    attack = AutomatedWebSocketsAttack(args.access_token_file, args.payloads_file, args.template_file)
    attack.run()
