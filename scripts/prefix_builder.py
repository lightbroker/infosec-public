'''
    Purpose:
        Create a list of all permutations of digits and lowercase letters.
        Helpful for subdomain enumeration and cloud bucket discovery.

    Usage:
        $ python ./prefix_builder.py 3 file/path.txt --repeat_alpha=True
        
    Parameters:
        1. Numeric argument specifies the length 
            of each permutation in the list.

        2. File path (string) specifies the target
            file for writing the resulting permutations.

        3. --repeat_alpha
            Create permutations with letter repetition (e.g., "aa1").
'''

import string
import sys
from itertools import permutations


perm_length = sys.argv[1]
file_path = sys.argv[2]
repeat_alpha = sys.argv[3]

if perm_length.isdigit() == False:
    print(f'"{perm_length}" is not a digit.')
    exit()

perm_length_int = int(perm_length)

def should_repeat_alpha():
    try:
        if not repeat_alpha.startswith('--repeat_alpha'):
            return False
        arg_value = repeat_alpha.split('=')[1]
        if arg_value == 'True':
            return True
        elif arg_value == 'False':
            return False
        else:
            return False
    except:
        return False

items = string.ascii_lowercase + string.digits

if should_repeat_alpha():
    print('repeating alpha')
    items = items + string.ascii_lowercase

with open(file_path, 'w') as list_file:
    for p in permutations(items, perm_length_int):
        perm = ''.join(p)
        list_file.write(f'{perm}\n')
