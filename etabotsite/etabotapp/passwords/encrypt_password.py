from Crypto.Cipher import AES
import keyring 

#gets encryptino jet from the keyring
#asks user for password to encrypt and returns encyrpted password
key = keyring.get_password('system','Jtest1')[:16]
print('using key of length {} symbols'.format(len(key)))
obj = AES.new(key, AES.MODE_CBC, 'This is an IV456')
message = input('enter JIRA password to encrypt:\n')
if len(message) != 16:
	message = message + ''.join([' ' for i in range(16 - len(message))])
ciphertext = obj.encrypt(message)
print('encrypted password:\n{}'.format(ciphertext))

