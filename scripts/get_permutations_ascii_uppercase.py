import itertools
from string import ascii_uppercase


char_space = ascii_uppercase
characters = list(char_space)

# for p in permutations(characters, 3):
with open('./permutations2.txt','at') as f:
    for p in itertools.product(characters, repeat=3):
        f.write(f'{p[0]}{p[1]}{p[2]}\n')
