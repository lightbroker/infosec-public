import string
import sys
from itertools import permutations


items = string.ascii_lowercase + string.digits
perm_length = sys.argv[1]

if perm_length.isdigit() == False:
    print(f'"{perm_length}" is not a digit.')
    exit()

perm_length_int = int(perm_length)

for p in permutations(items, perm_length_int):
    print(''.join(p))
