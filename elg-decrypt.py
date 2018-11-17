import sys, re, os, hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import (
    Cipher, algorithms, modes
)

def pow_x(g_base,a,p_mod):
  x=1
  bits = "{0:b}".format(a)
  for i, bit in enumerate(bits):
    if bit=='1':
        x = (((x**2)*g_base)%p_mod)
    elif bit=='0':
        x = ((x**2)%p_mod)
  return x%p_mod

def decrypt(key, associated_data, iv, ciphertext, tag):
    # Construct a Cipher object, with the key, iv, and additionally the
    # GCM tag used for authenticating the message.
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()

    # We put associated_data back in or the tag will fail to verify
    # when we finalize the decryptor.
    decryptor.authenticate_additional_data(associated_data)

    # Decryption gets us the authenticated plaintext.
    # If the tag does not match an InvalidTag exception will be raised.
    return decryptor.update(ciphertext) + decryptor.finalize()

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as my_file1:
        cipherfile = my_file1.readlines()
        m = cipherfile[0].split(',')[0]
        pattern = re.findall('\d+', m)
        gb = int(pattern[0])
        n = cipherfile[0].split(',')[1]
        pattern = re.findall('\S+', n)
        ciphertext_in_bytes = bytes.fromhex(pattern[0])

    with open(sys.argv[2], 'r') as my_file2:
        secret = my_file2.readlines()
        x = secret[0].split(',')[0]
        pattern = re.findall('\d+', x)
        p = int(pattern[0])
        y = secret[0].split(',')[1]
        pattern = re.findall('\d+', y)
        g = int(pattern[0])
        z = secret[0].split(',')[2]
        pattern = re.findall('\d+', z)
        a = int(pattern[0])

    ga = pow_x(g, a, p)
    gab = pow_x(gb, a, p)
    raw_key = str(ga) + " " + str(gb) + " " + str(gab)
    key = hashlib.sha256()
    key.update(raw_key.encode())

    associated_data = "Here is a string to add random associated data"

    plaintext = decrypt(key.digest(), associated_data.encode(), ciphertext_in_bytes[:16], ciphertext_in_bytes[16:(len(ciphertext_in_bytes) - 16)], ciphertext_in_bytes[(len(ciphertext_in_bytes) - 16):]).decode()
    if plaintext:
        print(plaintext)
    else:
        print("Error")