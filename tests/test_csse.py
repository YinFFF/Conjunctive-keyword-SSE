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
Tests the correctness of the implementation of multi-keyword conjunctive SSE.
"""
# Path hack
import sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(1, os.path.abspath('..'))

import random
#from fhipe import ipe
from csse import csse
from shve import shve
import math
import time
from csse import IBF
from memory_profiler import profile

# @profile
def print_memroy():
  return

def test_new_solution(file_vec_list, query_keywords_index, dic_num):
  print_memroy()
  # generate index
  start_time = time.time()
  scheme = csse.NewSolution(file_vec_list)
  end_time = time.time()
  print("index build time:", end_time - start_time)

  # generate trapdoor
  # the last element of query_vec should be -query_num
  start_time = time.time()
  query_vec = ['*'] * dic_num
  for i in query_keywords_index:
    query_vec[i] = 1
  trap = scheme.genTrapdoor(query_vec)

  # search
  search_result = scheme.search(trap, query_vec)
  # print("seach_result:", search_result)
  end_time = time.time()
  print("query time:", end_time - start_time)

  print_memroy()

def test_old_solution(file_vec_list, query_keywords_index, dic_num):

  print_memroy()
  # generate index
  start_time = time.time()
  scheme = csse.OldSolution1(file_vec_list)
  end_time = time.time()
  print("index build time:", end_time - start_time)

  start_time = time.time()
  # generate trapdoor
  # the last element of query_vec should be -query_num
  # query_vec = [0] * (dic_num + 1)
  # for i in query_keywords:
  #   query_vec[i] = 1
  trap = scheme.genTrapdoor(query_keywords_index)

  # search
  search_result = scheme.search(trap)
  # print("search_result:", search_result)
  end_time = time.time()
  print("query time:", end_time - start_time)
  print_memroy()

if __name__ == '__main__':
  # initial files parameters
  dic_num = 1000
  dic_num_in_one_file = dic_num // 10
  file_num = 5000
  # query_keywords_num = 10

  # generate files 
  file_vec_list = []
  csse.GenFileVector(file_num, dic_num, file_vec_list, dic_num_in_one_file)


  # query_keywords_index = [1, 2, 3, 4, 7, 10, 12, 15] 
  # query_keywords_index = [1, 5] 
  # print("queried keywords:", query_keywords_index)

  # for i in range(len(file_vec_list)):
  #   print("file ", i, ":", file_vec_list[i])


  for query_keywords_num in range(50, 100, 10):
    # initial a set to store query keywords 
    query_keywords_index = []
    for i in range(query_keywords_num):
      while True:
        temp_ind = random.randint(0, dic_num - 1)
        if temp_ind not in query_keywords_index:
          query_keywords_index.append(temp_ind)
          break

    print("=================", "query_keywords_num:", query_keywords_num, "====================")
    print("old solution")
    test_old_solution(file_vec_list, query_keywords_index, dic_num)
    print("new solution")
    test_new_solution(file_vec_list, query_keywords_index, dic_num)

  '''
  file_vec = [1, 1, 0, 0, 1, 1, 1, 1, 1, 1]

  query_vec = [1, 1, '*', 0, '*', '*', '*', '*', '*', 1]

  scheme = shve.SHVE()

  c = scheme.Enc(file_vec)

  (d0, d1, S) = scheme.kenGen(query_vec)

  print(scheme.Query(d0, d1, S, c))
  '''

  '''
  m = 5000
  k = 5
  bf = IBF.InsBloomFilter(m, k)

  test_val_list = []
  for i in range(1000):
    temp_val = os.urandom(16)
    test_val_list.append(temp_val)

  for i in range(len(test_val_list)):
    if i % 2 == 0:
      bf.add(test_val_list[i])

  true_num = 0
  for i in range(len(test_val_list)):
    if test_val_list[i] in bf:
      true_num += 1

  print(true_num)
  '''