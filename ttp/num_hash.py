#! /usr/bin/python
# -*- coding: latin-1 -*-
"""

$Id: num_hash.py 68 2004-08-12 11:24:43Z mtr $

Copyright (C) 2004 by Martin Thorsen Ranang
"""

__version__ = "$Rev: 68 $"

n2a_map = {}
for i in range(36):
    if i < 10:
        n2a_map[i] = '%s' % i
    else:
        n2a_map[i] = chr(ord('a') + i - 10).lower()

a2n_map = {}
for k, v in n2a_map.items():
    a2n_map[v] = k


def num2alpha(m):

    """ Recursively convert (positive) M from decimal to base
    'len(n2a_map)'. """
    
    n = len(n2a_map)
    
    if (m < n): 
        return '%s' % n2a_map[m]
    else:
        return '%s%s' % (num2alpha(m / n), n2a_map[m % n])

def alpha2num(str):

    """ Convert STR from base 'len(n2a_map)' into decimal. """
    
    # Convert every high-based digit into a decimal number.
    
    L = [a2n_map[i] for i in str]
    
    # Reverse the sequence.
    
    L.reverse()
    
    # Simply return the sum of the constituents l_i * (27 ** i) of L.

    p = len(a2n_map)
    return reduce(lambda x, y: y + x,
                  [(x * pow(p, i)) for i, x in enumerate(L)])

    
def main ():

    """ Module mainline (for standalone execution).  If called from
    the command line, perform some tests... """
    
    import sys
    
    if len(sys.argv) < 2:
        R = range(0, 100000)
    else:
        R = [int(sys.argv[1])]
        
    print 'Testing...',
    sys.stdout.flush()
        
    for i in R:
        x = num2alpha(i)
        j = alpha2num(x)
        
        if i != j:
            print 'Error!!!'

    if len(R) == 1:
        print 
        print 'i =', i
        print 'x =', x
        print 'j =', j
        
    print 'done'

    print alpha2num('zzzz')
    return

class HashKeys(object):

    def __init__(self, max_key):
        self.N = alpha2num(max_key)
        self.bitmap = 1L << self.N

        
    def next(self):
        pass
    
    
if __name__ == "__main__":
    #h = HashKeys('zzzz')
    
    #print h.next()
    
    main ()
