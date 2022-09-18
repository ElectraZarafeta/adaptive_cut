import pickle

def save_dict(dictname, filename):
    f = open(filename,"wb")

    pickle.dump(dictname,f)

    f.close()


def load_dict(filename):
    file = open(filename, "rb")

    return pickle.load(file)
    

def Dc(m, n):
    try:
        return (m * (m - n + 1.0)) / ((n - 2.0) * (n - 1.0))
    except ZeroDivisionError:
        return 0.0

def swap(a,b):
    if a > b:
        return b,a
    return a,b