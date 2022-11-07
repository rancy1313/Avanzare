h = "4.56"

j = h.split('.')
print("j ", j)
k = []

for x in j:
    k.append(int(x) * 3)

print(k)


n = k[1] % 100
print(n)
m = int(k[1] / 100)
print(m)

k[0] = str(k[0] + m)
k[1] = str(n)
sep = "."
print("test", sep.join(k))

def deciaml_add(num, quantity):
    num = str(num)
    num = num.split('.')
    print("inside  func: ", num)
    lst =[]
    for x in num:
        lst.append(int(x) * quantity)
    lst[0] = str(lst[0] + (int(lst[1] / 100)))
    lst[1] = str(lst[1] % 100)
    tmp = '.'.join(lst)
    return tmp

n = deciaml_add(243.99, 5)
print(n)

def deciaml_taxes(num, quantity):
    num = str(num)
    num = num.split('.')
    lst = []
    for x in num:
        lst.append((100*int(x)) * 8)
    return tmp