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
Tests the correctness of the implementation of IPE and two-input functional 
encryption.
"""

# Path hack
import sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(1, os.path.abspath('..'))

import random
from fhipe import ipe, tife

def test_ipe():
  """
  Runs a test on IPE for toy parameters.
  """

  n = 5
  M = 20
  # x = [random.randint(0, M) for i in range(n)]
  # y = [random.randint(0, M) for i in range(n)]
  x = [1, 1, 1, 1, -4]
  y = [1, 1, 1, 1, 1]
 
  checkprod = sum(map(lambda i: x[i] * y[i], range(n)))
  print("x:", x)
  print("y:", y)
  print("checkprod:", checkprod)

  (pp, sk) = ipe.setup(n)
  skx = ipe.keygen(sk, x)
  cty = ipe.encrypt(sk, y)
  prod = ipe.decrypt(pp, skx, cty, 0)
  # print("result", result)
  print("prod", prod)
  assert prod == checkprod, "Failed test_ipe"

def test_tife():
  """
  Runs a test on two-input functional encryption for the comparison function on 
  toy parameters.
  """

  N = 30
  f = lambda x,y: 1 if x < y else 0

  x = random.randint(0, N-1)
  y = random.randint(0, N-1)

  (pp, sk) = tife.setup(N, f)
  ctx = tife.encryptL(sk, x)
  cty = tife.encryptR(sk, y)
  result = tife.decrypt(pp, ctx, cty)
  assert result == f(x,y), "Failed test_tife"

test_ipe()
# test_tife()
