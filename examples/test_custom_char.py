"""
  test_clear.py test example for the M66004 VFD Driver.

  - Focus: write chars SPACE on digits 1 to 16 to clear the content!
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
from vfd_m66 import VFD_M6604, RAM1
VFD_LEN = 16

_reset = Pin(Pin.board.GP18, Pin.OUT, value=True ) # Unactive
_cs = Pin( Pin.board.GP14, Pin.OUT, value=True ) # unactiva
_sdata = Pin( Pin.board.GP13, Pin.OUT )
_sck = Pin( Pin.board.GP16, Pin.OUT, value=True )

vfd =VFD_M6604( sck=_sck, sdata=_sdata, cs=_cs, reset=_reset )
vfd.digit_length( VFD_LEN )
vfd.normal_operation()

# We can define 5x7 custom char from RAM1 to RAM16
vfd.define_char( RAM1,
	  [ 0b00000,
		0b01010,
		0b10101,
		0b10001,
		0b01010,
		0b00100,
		0b00000 ] )

vfd.display_digit( 1, True ) # Set position from 1th digit with auto-increment
vfd.send( bytes( [ RAM1, RAM1, RAM1 ] ))  # send null chars
