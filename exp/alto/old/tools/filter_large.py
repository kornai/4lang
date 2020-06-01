import sys

for line in sys.stdin:
    if line.count('/') > int(sys.argv[1]):
        continue
    print(line.strip())
