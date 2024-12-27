"""
  test_single_digit.py test example for the M66004 VFD Driver.

  - Focus: write possible char value on a given digit. Great to detect special 
           symbol and its values (assigned to a given digit position).
  - VFD Model: all

The MIT License (MIT)
Copyright (c) 2024 Dominique Meurisse, support@mchobby.be, shop.mchobby.be

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from machine import Pin
from vfd_m66 import VFD_M6604
import time

VFD_LEN = 16  # Nbr of Digits in the display
VFD_DIGIT = 16  # Digit index from 1..16


def chain(*iterables):
    for it in iterables:
        for element in it:
            yield element

_reset = Pin(Pin.board.GP18, Pin.OUT, value=True ) # Unactive
_cs = Pin( Pin.board.GP14, Pin.OUT, value=True ) # unactiva
_sdata = Pin( Pin.board.GP13, Pin.OUT )
_sck = Pin( Pin.board.GP16, Pin.OUT, value=True )

vfd =VFD_M6604( sck=_sck, sdata=_sdata, cs=_cs, reset=_reset )
vfd.digit_length( VFD_LEN )
vfd.normal_operation()
vfd.display_digit( VFD_DIGIT, False ) # Set position from 1th digit with no-increment
for ch in chain( [ch_idx for ch_idx in range( 32,128 )], [ch_idx for ch_idx in range( 160,224 )]  ):
	vfd.send( bytes( [ch] ))  # send null chars
	time.sleep_ms(100)



