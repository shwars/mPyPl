# File utilities

def readlines(fn):
    """
    Read all lines from a file into a list
    :param fn: filename
    :return: list of lines from the file
    """
    with open(fn) as f:
        content = f.readlines()
    return [x.strip() for x in content]

def writelines(fn,lst):
    """
    Writes all lines in a given list to a text file
    :param fn: filename
    :param lst: list of strings
    """
    with open(fn,'w') as f:
        for s in lst:
            f.write(s+'\n')
