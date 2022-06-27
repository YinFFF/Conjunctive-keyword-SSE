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
Obtains micro-benchmarks for the running times and parameter sizes of IPE and 
two-input functional encryption.
"""

# Path hack.
import sys, os, math
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(1, os.path.abspath('..'))

import random, time, zlib
from fhipe import ipe, tife

def list_tuple_mean(L):
  avgs = [0] * len(L[0])
  for tup in L:
    for i in range(len(tup)):
      avgs[i] += tup[i]
  for i in range(len(avgs)):
    avgs[i] /= len(L)
  return avgs

def bench_ipe(n, group_name, iter = 10, simulated = False, M = 1):
  setup_a = time.time()
  (pp, sk) = ipe.setup(n, group_name, simulated)
  setup_b = time.time()
 
  L = []
  for index in range(iter):
    x = [random.randint(0, M) for i in range(n)]
    y = [random.randint(0, M) for i in range(n)]
   
    keygen_a = time.time()
    skx = ipe.keygen(sk, x)
    keygen_b = time.time()
    
    encrypt_a = time.time()
    cty = ipe.encrypt(sk, y)
    encrypt_b = time.time()

    ctsize = get_ct_size(cty)

    decrypt_a = time.time()
    prod = ipe.decrypt(pp, skx, cty, M*M*n)
    decrypt_b = time.time()

    L.append((keygen_b - keygen_a, encrypt_b - encrypt_a, decrypt_b - decrypt_a, 
        ctsize))
  print("raw runtimes for each iteration: ", L)

  return (setup_b - setup_a, list_tuple_mean(L))

def bench_tife(N, group_name, iter = 10, simulated = False):
  f = lambda x,y: 1 if x < y else 0
  
  setup_a = time.time()
  (pp, sk) = tife.setup(N, f, group_name, simulated)
  setup_b = time.time()
  
  L = []
  for index in range(iter):
    x = random.randint(0, N-1)
    y = random.randint(0, N-1)

    encryptL_a = time.time()
    ctx = tife.encryptL(sk, x)
    encryptL_b = time.time()
    encryptR_a = time.time()
    cty = tife.encryptR(sk, y)
    encryptR_b = time.time()
    decrypt_a = time.time()
    result = tife.decrypt(pp, ctx, cty)
    decrypt_b = time.time()

    ctsize = get_ct_size(cty)

    L.append((encryptL_b - encryptL_a, encryptR_b - encryptR_a, decrypt_b - 
        decrypt_a, ctsize))
  print("raw runtimes for each iteration: ", L)

  return (setup_b - setup_a, list_tuple_mean(L))

def get_time_latex(x):
  units = 's'
  if x < 1:
    x *= 1000;
    units = 'ms'
  return ('$%.1f' % x) + '$' + units

def get_size_latex(x):
  units = 'B'
  format_str = '%d'
  if x > 1024:
    x /= 1024
    format_str = '%.1f'
    units = 'KB'
  if x > 1024:
    x /= 1024
    format_str = '%.1f'
    units = 'MB'
  return (('$' + format_str) % x) + '$' + units

def bench_iter(f, params_list):
  ret = []
  start_time = time.time()
  for p in params_list:
    print(f.__name__, p, "time: " + ("%.2fs" % (time.time() - start_time)))
    (setup_time, li_times) = f(p) if type(p) is int else f(*p)
    print((setup_time, li_times))

    s = li_times

    for i in range(len(s)):
      if i < len(s) - 1:
        s[i] = get_time_latex(s[i])
      else:
        s[i] = get_size_latex(s[i])
    
    ret.append(s)
  return ret

def get_ct_size(ct):
  ct_sizeinbytes = 0
  for elem in ct:
    elem_sizeinbytes = 0
    # extract integers from elem
    str_rep = ''.join(filter(lambda c: c == ' ' or c.isdigit(), str(elem)))
    delim_size = len(str(elem)) - len(str_rep) # number of delimiter characters
    elem_sizeinbytes += delim_size
    L = [int(s) for s in str_rep.split()]
    for x in L:
      intsize = int(math.ceil(math.log2(x) / 8))
      elem_sizeinbytes += intsize
    ct_sizeinbytes += elem_sizeinbytes
  return ct_sizeinbytes

def gen_latex_table(filename):
  L_N = [5, 10, 30, 50, 100, 500, 1000]
  secparams = {80: "MNT159", 112: "MNT224"}
  iter = 10
  simulated = True

  F = open(filename, "w")
  for lam in secparams:
    L_ipe = bench_iter(bench_ipe,
        [(i, secparams[lam], iter, simulated) for i in L_N])
    L_tife = bench_iter(bench_tife,
        [(i, secparams[lam], iter, simulated) for i in L_N])
    for i in range(len(L_N)):
      F.write("$%d$ & $%d$ & %s & %s & %s & %s & %s & %s & %s & %s \
      \\\\\n" % ((lam, L_N[i]) + tuple(L_ipe[i]) + tuple(L_tife[i])))
    F.write("\\midrule\n")
  F.close()

gen_latex_table("latex-table.out")
