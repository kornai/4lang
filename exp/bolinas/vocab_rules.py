import sys

def main():
    for line in sys.stdin:
        word = line.strip()
        print "X -> (. :{0}) | (. :{0});".format(word)

main()

