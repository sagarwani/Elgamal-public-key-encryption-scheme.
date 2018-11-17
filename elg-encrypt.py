import os, sys, random, re, hashlib
from random import randrange, getrandbits
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

def check_prime(n, k=128):

    # First need to test if n is even.
    # 2 is a safe prime that can be used.
    if n == 2 or n == 3:
        return True
    if n <= 1 or n % 2 == 0:
        return False
    # To find r and s
    s = 0
    r = n - 1
    while r & 1 == 0:
        s += 1
        r //= 2
    # do k tests
    for _ in range(k):
        a = randrange(2, n - 1)
        x = pow_x(a, r, n)
        if x != 1 and x != n - 1:
            j = 1
            while j < s and x != n - 1:
                x = pow_x(x, 2, n)
                if x == 1:
                    return False
                j += 1
            if x != n - 1:
                return False
    return True

def encrypt(key, plaintext, associated_data):
    # Generate a random 96-bit IV.
    iv = os.urandom(16)
    # Construct an AES-GCM Cipher object with the given key and a
    # randomly generated IV.
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()

    # associated_data will be authenticated but not encrypted,
    # it must also be passed in on decryption.
    encryptor.authenticate_additional_data(associated_data)

    # Encrypt the plaintext and get the associated ciphertext.
    # GCM does not require padding.
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    return (iv, ciphertext, encryptor.tag)

if __name__ == '__main__':
    with open(sys.argv[2], 'r') as my_file1:
        secret = my_file1.readlines()
        x = secret[0].split(',')[0]
        pattern = re.findall('\d+', x)
        p = int(pattern[0])
        y = secret[0].split(',')[1]
        pattern = re.findall('\d+', y)
        g = int(pattern[0])
        z = secret[0].split(',')[2]
        pattern = re.findall('\d+', z)
        ga = int(pattern[0])

        q = int((p - 1) / 2)
        while not check_prime(q):
            q -= 1
        b = random.randint(2, q - 1)
        gb = pow_x(g, b, p)
        gab = pow_x(ga, b, p)

        raw_key = str(ga) + " " + str(gb) + " " + str(gab)
        key = hashlib.sha256()
        key.update(raw_key.encode())

        message = sys.argv[1]
        message = message.replace('"', '')

        associated_data = "Here is a string to add random associated data"
        iv, ciphertext, tag = encrypt(key.digest(), message.encode(), associated_data.encode())
        final_cipher = iv + ciphertext + tag

        with open(sys.argv[3], 'w') as my_file3:
            my_file3.write('( %d, %s )' % (gb, final_cipher.hex()))

