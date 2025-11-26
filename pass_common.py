#We are using secrets now

import secrets
import string

password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
print(password)