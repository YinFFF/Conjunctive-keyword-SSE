import os
import hmac

class InsBloomFilter(object):
    
    def __init__(self, bf_size:int, key_num:int):
        
        self.bf = [0] * bf_size

        self.key = []
        for i in range(key_num):
            self.key.append(os.urandom(16))
    
    def add(self, e:bytes):
        
        for key in self.key:
            h = hmac.new(key, e, 'MD5') 
            self.bf[int.from_bytes(h.digest(), 'big') % len(self.bf)] = 1
        
    def __contains__(self, e:bytes) -> bool:
        
        for key in self.key:
            h = hmac.new(key, e, 'MD5')
            if self.bf[int.from_bytes(h.digest(), 'big') % len(self.bf)] == 0:
                return False
        
        return True