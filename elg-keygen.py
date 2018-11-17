from random import randrange, getrandbits
import random, sys

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

def generate_prime_candidate(l):
    # generating the random bits here
    p = getrandbits(l)
    # set MSB and LSB to 1 by applying mask
    p |= (1 << l - 1) | 1
    return p

def generate_prime_number(l=1023):
    p = 4
    while not check_prime(p, 128):
        p = generate_prime_candidate(l)
    return p


if __name__ == '__main__':

    big_primeq = generate_prime_number()
    j = 2
    big_primep = j*big_primeq + 1
    while not check_prime(big_primep):
        big_primep += 2
    generator = 1
    while generator == 1:
        h = random.randint(2, big_primep - 1)
        generator = pow_x(h, j, big_primep)
    a = random.randint(2, big_primeq - 1)
    ga = pow_x(generator, a, big_primep)
    with open(sys.argv[1], 'w') as my_file1:
        my_file1.write('( %d, %d, %d )' % (big_primep, generator, ga))
    with open(sys.argv[2], 'w') as my_file2:
        my_file2.write('( %d, %d, %d )' % (big_primep, generator, a))