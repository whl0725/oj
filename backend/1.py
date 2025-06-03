klo = []
for i in range(10):
    t = int(input())
    klo.append(t)

klo.sort()
print(' '.join(map(str, klo)))