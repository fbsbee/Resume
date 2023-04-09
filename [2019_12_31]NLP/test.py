if False :
    print('aa')
if 43 :
    print('asdf')
a = ['1','2','3','4']
b = ['3', '4']
a = set(a) - set(b)
print( sorted(list(a) ) )

# import pandas as pd
# a = pd.DataFrame()
# a.to_csv(sep='\t')

a = {1:1}
print(a.keys())
b = {a : None for a in a.keys()}
print(b)
a= '1234'
print(a[len(a):])

a= ['123', 'ab13', 'a123b']
# for b in a:
#     if '12' in b:
#         print('hello')

a = '3'
b = ['12', '34', '56']
print(''.join(b))
c = ''.join(b)
if a in c:
    print('a,',a)
    print('laksdjflaksdjflkasdjflk')

for num, c in enumerate(b) :
    if a in c:
        print(num)
        print(b[num:])
        
if a in b:
    print('hellasdfasdf')

import numpy as np

# b = np.ones(5, 3)
# a = np.eye(3, 5)
# print(np.dot(a,b ))

# def a(b=1):
#     return b
# 1.0
a = 1
b= 1.0
print(a.__class__)
print(b.__class__)


# print(a())

# print(a(1))
