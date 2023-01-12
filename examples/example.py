import logging
import sys
sys.path.append('../pysensorpro/')

import pysensorpro

# We can insert a chain of callbacks to process / enrich the data
# The callback needs to return an event to be processed down the chain

def test_callback(event):
    print('Test Callback Invoked')
    return event

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    pysensorpro.add_callback(test_callback)
    pysensorpro.Start()
