import bcrypt
import string

passwd = u'💩💩💩💩💩💩💩💩💩💩💩💩💩💩💩'  # randomly generated
hashed_passwd = u'$2b$05$jg0N2fw9xEFt4AMxEEc.ducKLrgOZ5cpohM9JLfMBusl8BJmWIQ5S'  # taken from sudo as adm user
allchars = string.printable
flag = 'aaH34vyR41n'

for c in allchars:
    testpasswd = passwd + flag + c
    if bcrypt.checkpw(testpasswd.encode('utf-8'), hashed_passwd.encode('utf-8')):
        print("match at " + c)

# 💩💩💩💩💩💩💩💩💩💩💩💩💩💩💩aa???????
# salt:H34vyR41n