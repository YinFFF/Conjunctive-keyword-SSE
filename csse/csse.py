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
The implementation of multi-keyword conjunctive SSE.
"""

# Path hack
import sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(1, os.path.abspath('..'))

import random
#from fhipe import ipe
from shve import shve
import math
from bloom_filter2 import BloomFilter
import hmac
from csse import IBF
# from memory_profiler import profile


class NewSolution(object):

  def __init__(self, vec_list):

    if len(vec_list) == 0:
      return

    # (self.pp, self.sk) = ipe.setup(len(vec_list[0]))
    self.shve_scheme = shve.SHVE()

    # use a array to represent the tree index
    self.enc_vec_list = [0] * (len(vec_list) * 2 - 1)

    first_leaf_ind = math.floor(len(self.enc_vec_list) / 2)

    # generate vector in leaf nodes
    for i in range(len(vec_list)):
      # self.enc_vec_list[first_leaf_ind + i] = ipe.encrypt(self.sk, vec_list[i])
      self.enc_vec_list[first_leaf_ind + i] = vec_list[i]
  
    # generate vector in non-leaf nodes
    for i in range(first_leaf_ind - 1, -1, -1):
      temp_vec = [0] * len(self.enc_vec_list[i * 2 + 1])
      for j in range(len(self.enc_vec_list[i * 2 + 1])):
        temp_vec[j] = self.enc_vec_list[i * 2 + 1][j] or self.enc_vec_list[i * 2 + 2][j]
      self.enc_vec_list[i] = temp_vec
    
    # for i in range(len(self.enc_vec_list)):
    #   print(i, ":", self.enc_vec_list[i])

    # encrypt 
    for i in range(len(self.enc_vec_list)):
      # self.enc_vec_list[i] = ipe.encrypt(self.sk, self.enc_vec_list[i])
      self.enc_vec_list[i] = self.shve_scheme.Enc(self.enc_vec_list[i])
    
  def genTrapdoor(self, query_vec):
    # return ipe.keygen(self.sk, query_vec)
    return self.shve_scheme.kenGen(query_vec)

  def search(self, trap, query_vec):

    first_leaf_ind = math.floor(len(self.enc_vec_list) / 2)

    search_result = []

    search_stack = [0]

    count = 0

    while len(search_stack):
      temp_ind = search_stack.pop()
      # if ipe.decrypt(self.pp, trap, self.enc_vec_list[temp_ind], 10) == 0:
      #generate a new trapdoor
      count += 1
      self.genTrapdoor(query_vec)
      if self.shve_scheme.Query(trap[0], trap[1], trap[2], self.enc_vec_list[temp_ind]) == True:
        if temp_ind >= first_leaf_ind:
          search_result.append(temp_ind - first_leaf_ind)          
        else:
          search_stack.append(temp_ind * 2 + 1)
          search_stack.append(temp_ind * 2 + 2)

    print("count = ", count)
    return search_result

class OldSolution1(object):
  # @profile 
  def __init__(self, vec_list: list) -> None:

    if len(vec_list) == 0:
      return

    # use a array to represent the tree index
    enc_vec_list = [0] * (len(vec_list) * 2 - 1)
    # self.bloom_list = [BloomFilter(10000, 0.01) for _ in range((len(vec_list) * 2 - 1))] 
    
    # according to the paper's recommendation,
    # bf_num / dic_num = 5 
    # key_num = bf / dic_num * ln(2)
    dic_num = len(vec_list[0])
    bf_num = dic_num * 5
    key_num = math.ceil(5 * math.log(2))
    self.bloom_list = [IBF.InsBloomFilter(bf_num, key_num) 
                       for _ in range((len(vec_list) * 2 - 1))] 

    # In the paper, bloom_list_backup is used to proof IND-CPA security.
    # In the code, bloom_list_backup is unused and just for evaluating real cost.
    self.bloom_list_backup = [IBF.InsBloomFilter(bf_num, key_num) 
                       for _ in range((len(vec_list) * 2 - 1))] 

    first_leaf_ind = math.floor(len(enc_vec_list) / 2)

    for i in range(len(vec_list)):
      # self.enc_vec_list[first_leaf_ind + i] = ipe.encrypt(self.sk, vec_list[i])
      enc_vec_list[first_leaf_ind + i] = vec_list[i]
  
    for i in range(first_leaf_ind - 1, -1, -1):
      temp_vec = [0] * len(enc_vec_list[i * 2 + 1])
      for j in range(len(enc_vec_list[i * 2 + 1])):
        temp_vec[j] = enc_vec_list[i * 2 + 1][j] or enc_vec_list[i * 2 + 2][j]
      enc_vec_list[i] = temp_vec
    
    # for i in range(len(self.enc_vec_list)):
    #   print(i, ":", self.enc_vec_list[i])

    # encrypt element through HMAC and add it to the bloom filter 
    self.hmac_key = b'TEST KEY'
    for i in range(len(enc_vec_list)):
      for j in range(len(enc_vec_list[i])):
        if enc_vec_list[i][j] == 1:
          h = hmac.new(self.hmac_key, j.to_bytes(2, 'big'), 'MD5') 
          hmac_val = h.digest()
          self.bloom_list[i].add(hmac_val)
          # self.bloom_list[i].add(val)
  
    return 

  def genTrapdoor(self, query_keywords:list):

    result = []

    for keyword in query_keywords:
      h = hmac.new(self.hmac_key, keyword.to_bytes(2, 'big'), 'MD5')
      hmac_val = h.digest()
      result.append(hmac_val)
      # result.append(keyword)

    return result
      
  def search(self, trap:list):

    first_leaf_ind = math.floor(len(self.bloom_list) / 2)

    search_result = []

    search_stack = [0]

    count = 0

    while len(search_stack):
      temp_ind = search_stack.pop()
      count += 1
      if self.isBloomFilterContainAllKeywords(self.bloom_list[temp_ind], trap) == 1:
        if temp_ind >= first_leaf_ind:
          search_result.append(temp_ind - first_leaf_ind)          
        else:
          search_stack.append(temp_ind * 2 + 1)
          search_stack.append(temp_ind * 2 + 2)
      
    print("count = ", count)
    return search_result

  def isBloomFilterContainAllKeywords(self, cur_bloom_filter, trap):

    result = 1

    for i in range(len(trap)):
      if trap[i] not in cur_bloom_filter:
        result = 0
        break
    
    return result

  '''
  class OldSolution1(object):
    
    def __init__(self, vec_list):

      # tranform files to the form of <w, id_set>
      self.

      # encrypt the list of <w, id_set> (i.e., Tset)

      # generate bloom filter for each file (i.e., Xset)
  '''

def GenFileVector(file_num, dic_num, file_vec_list, dic_num_in_one_file):
  '''
  initial file_num vectors and group them to a list, i.e., vile_vec_list

  for each vector, the last element is set to 1 for the search process later
  '''
  for i in range(file_num):

    temp_file_vec = [0] * dic_num
    # temp_file_vec[-1] = 1

    count = dic_num_in_one_file
    while count > 0:
      temp_ind = random.randint(0, dic_num - 1)
      if temp_file_vec[temp_ind] == 0:
        temp_file_vec[temp_ind] = 1
        count -= 1
        
    file_vec_list.append(temp_file_vec)
    
