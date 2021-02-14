
def parseint(s, base=10):
    try:
        return int(s, base=base)
    except ValueError:
        return 0

