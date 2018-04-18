from __future__ import print_function
import random

"""
Each Block is represented by Notations as follows

     3
   -----
  '     '
4 '  A  ' 2
  '     '
  '-----'
     1
"""

C = { 'A1': 3,  'B1': 3,  'C1': 3,  'D1': 3,  'E1': 3,
      'A2': 1,  'B2': 1,  'C2': 1,  'D2': 1,  'E2': 6,
      'A3': 3,  'B3': 3,  'C3': 3,  'D3': 3,  'E3': 3,
      'A4': 1,  'B4': 1,  'C4': 1,  'D4': 1,  'E4': 6,

      'F1': 3,  'G1': 3,  'H1': 3,  'I1': 3,  'J1': 6,
      'F2': 6,  'G2': 6,  'H2': 1,  'I2': 1,  'J2': 1,
      'F3': 3,  'G3': 3,  'H3': 3,  'I3': 3,  'J3': 6,
      'F4': 6,  'G4': 6,  'H4': 1,  'I4': 1,  'J4': 1,

      'K1': 3,  'L1': 3,  'M1': 3,  'N1': 3,  'O1': 3,
      'K2': 1,  'L2': 1,  'M2': 6,  'N2': 1,  'O2': 1,
      'K3': 3,  'L3': 3,  'M3': 3,  'N3': 3,  'O3': 3,
      'K4': 1,  'L4': 1,  'M4': 6,  'N4': 1,  'O4': 1,
    }

Values = [[] for i in range(5)] # Values = [[], [], [], []]
Blocks = [[] for i in range(5)] # Blocks = [[], [], [], []]
Vars = [chr(i)+str(j) for i in range(65,80) for j in range(1,5)]
Flag = list(range(60))
Sum = 83

random.seed(9698727450)
ix = 0
Value = Values[ix]
Block = Blocks[ix]

while True:

    j = random.choice(Flag)
    Flag.remove(j)
    val = C[Vars[j]]

    if sum(Value) < Sum:
        Value.append(val*2)
        Block.append(Vars[j])
    if sum(Value) > Sum:
        Excess = sum(Value) - Sum
        Value[-1] -= Excess
        ix += 1
        Value, Block = Values[ix], Blocks[ix]
        Value.append(Excess)
        Block.append(Vars[j])
    elif sum(Value) == Sum:
        ix += 1
        Value, Block = Values[ix], Blocks[ix]
    if ix == 4:
        break

Blocks, Values = Blocks[:-1], Values[:-1]

for i in Blocks:
    print(*i, sep='-> ')
