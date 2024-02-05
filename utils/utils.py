# utils.py

def is_integer(s):
    try:
        int(s)
        if int(s) < 0:
            return False
        return True
    except ValueError:
        return False
