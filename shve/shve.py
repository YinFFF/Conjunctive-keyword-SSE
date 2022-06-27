"""
Copyright (c) 2016, Kevin Lewi
 
Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
"""

"""
Implementation of symmetric hidden vector encryption (SHVE).
"""

import sys, os, math
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def byte_xor(ba1, ba2):
  if len(ba1) > len(ba2):
    ba2 = b'\x00' * (len(ba1) - len(ba2)) + ba2
  elif len(ba2) > len(ba1):
    ba1 = b'\x00' * (len(ba2) - len(ba1)) + ba1

  return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])
  
def PRF(msk, m):

  if len(m) % 16 != 0:
    m = m + b'\x00' * (16 - (len(m) % 16))

  cipher = Cipher(algorithms.AES(msk), modes.ECB(), default_backend())

  encryptor = cipher.encryptor()

  c = encryptor.update(m) + encryptor.finalize()

  return c

def SYE(K, m):

  iv = os.urandom(16)

  cipher = Cipher(algorithms.AES(K), modes.CBC(iv), default_backend())

  encryptor = cipher.encryptor()

  c = encryptor.update(m) + encryptor.finalize()

  return (c, iv)

def SYD(K, c, iv):

  cipher = Cipher(algorithms.AES(K), modes.CBC(iv), default_backend())

  decryptor = cipher.decryptor()
  
  m = decryptor.update(c) + decryptor.finalize()

  return m

class SHVE(object):
  
  def __init__(self) -> None:

    # msk is 16*8 = 128 bits
    self.msk = os.urandom(16)

  def kenGen(self, v:list):

    S = []

    self.K = os.urandom(16)
    # print("K:", self.K)

    xor_PRF = b'\x00' * 16
    for i in range(len(v)):
      if v[i] != '*':
        S.append(i)
        temp_PRF = PRF(self.msk, v[i].to_bytes(1, 'big') + i.to_bytes((i.bit_length() + 7) // 8, 'big'))
        xor_PRF = byte_xor(xor_PRF, temp_PRF)
    
    d0 = byte_xor(xor_PRF, self.K)

    d1 = SYE(self.K, b'\x00' * 16)
    
    return (d0, d1, S)

  def Enc(self, x:list):

    c = []

    for i in range(len(x)):
      c.append(PRF(self.msk, x[i].to_bytes(1, 'big') + i.to_bytes((i.bit_length() + 7) // 8, 'big')))

    return c

  def Query(self, d0, d1, S, c):

    xor_PRF = b'\x00' * 16
    for i in S:
      xor_PRF = byte_xor(xor_PRF, c[i])
    
    K = byte_xor(xor_PRF, d0)

    u = SYD(K, d1[0], d1[1])
    
    if u == b'\x00' * 16:
    # if K == self.K:
      return True
    else:
      return False
    
    

        
    

