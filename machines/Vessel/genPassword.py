from PySide2.QtCore import *


def genPassword():
    length = 32
    char = 0
    if char == 0:
        charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890~!@#$%^&*()_-+={}[]|:;<>,.?'
    else:
        if char == 1:
            charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        else:
            if char == 2:
                charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
            else:
                pass
    try:
        qsrand(QTime.currentTime().msec())
        password = ''
        for i in range(length):
            idx = qrand() % len(charset)
            nchar = charset[idx]
            password += str(nchar)
    except:
        print('error')
    return password


def gen_possible_passes():
    passes = []
    try:
        while True:
            ps = genPassword()
            if ps not in passes:
                passes.append(ps)
                # print(ps)
                print(len(passes))
    except KeyboardInterrupt:
        with open('pass.txt', 'a') as ofile:
            for p in passes:
                ofile.write(p + '\n')


gen_possible_passes()
