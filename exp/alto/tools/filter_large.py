import sys

for line in sys.stdin:
    if len(line.split()) > int(sys.argv[1]):
        continue
    print(line.strip())
