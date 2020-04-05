import math
a = 3
b = 0

BASE_EARNED_NTD = 150
NTD_GAP = 50
NTD_PER_POINTS = 0.7

a_earned_NTD = BASE_EARNED_NTD + math.ceil(a * NTD_PER_POINTS / NTD_GAP) * NTD_GAP
b_earned_NTD = BASE_EARNED_NTD + math.ceil(b * NTD_PER_POINTS / NTD_GAP) * NTD_GAP

print(a_earned_NTD)
print(b_earned_NTD)

