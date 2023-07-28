'''
    Creates a list of either HTML- or URL-encoded values based on specified repeitions and a provided string value.
    Useful for creating Burp Intruder payloads.

    Usage:
        $ python serial_encoder.py [encoding] [repetitions] [value]

    Author: 
        adam wilson
        https://github.com/lightbroker

    Example Command:
        $ python3 ./serial_encoder.py -u 3 "<div>test</div>"
    
    Example Output:
        <div>test</div>
        %3Cdiv%3Etest%3C/div%3E
        %253Cdiv%253Etest%253C/div%253E
        %25253Cdiv%25253Etest%25253C/div%25253E
'''

import calendar
import html
import sys
import time
import urllib.parse


# command line args
encoding_arg = sys.argv[1]
repetitions_arg = sys.argv[2]
value = sys.argv[3]

print(encoding_arg)
print(repetitions_arg)
print(value)

# defaults
results_filename = ''
repetitions = 0
use_html_encoding = False
use_url_encoding = False
timestamp = calendar.timegm(time.gmtime())

# validate encoding arg
if encoding_arg == '-h':
    use_html_encoding = True
elif encoding_arg == '-u':
    use_url_encoding = True
else:
    print('Encoding invalid or not specified.')
    exit()

# repetitions argument must be a digit
if repetitions_arg.isdigit() == False:
    print(f'"{repetitions_arg}" is not a digit.')
    exit()
else:
    repetitions = int(repetitions_arg)

def write_line(value):
    with open(results_filename, 'at') as list_file:
        list_file.write(f'{value}\n')

def html_encode(value, repetitions):
    while (repetitions > 0):
        value = html.escape(value)
        write_line(value)
        repetitions -= 1

def url_encode(value, repetitions):
    while (repetitions > 0):
        value = urllib.parse.quote(value)
        write_line(value)
        repetitions -= 1

if use_html_encoding == True:
    results_filename = f'htmlencoded_payloads_{timestamp}.txt'
    write_line(value)
    html_encode(value, repetitions)

if use_url_encoding == True:
    results_filename = f'urlencoded_payloads_{timestamp}.txt'
    write_line(value)
    url_encode(value, repetitions)
