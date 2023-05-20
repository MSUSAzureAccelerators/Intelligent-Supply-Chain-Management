# Next run the following commands to encode(this assumes a fresh state)
# This is autility for Key Vault
import base64
encoded = base64.b64encode(b'YOUR_APP_SECRET')

#print our value
print(encoded)
