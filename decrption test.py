from Crypto.Cipher import AES

# read encrypted data from file
with open('keystrokes_encrypted.bin', 'rb') as f:
    data = f.read()

# AES key
key = b'mysecretkey123456789123456789123'

# decrypt data
iv = data[:AES.block_size]
cipher = AES.new(key, AES.MODE_CBC, iv)
decrypted_data = cipher.decrypt(data[AES.block_size:])

# remove padding
padding_size = decrypted_data[-1]
decrypted_data = decrypted_data[:-padding_size]

# write decrypted data to file
with open('keystrokes_decrypted.txt', 'wb') as f:
    f.write(decrypted_data)
