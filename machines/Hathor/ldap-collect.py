import ldap3
server = ldap3.Server('hathor.htb', get_info=ldap3.ALL, port=636, use_ssl=True)
conn = ldap3.Connection(server)
conn.bind()
print(server.info)
