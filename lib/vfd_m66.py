
"""
  vfd_m66.py is a micropython module for M66004 VFD driver (Vaccum Fluorescent Display)

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
import time
from micropython import const

RAM1 = const(144) # Char index in Ansi table
RAM2 = const(145)
RAM3 = const(146)
RAM4 = const(147)
RAM5 = const(148)
RAM6 = const(149)
RAM7 = const(150)
RAM8 = const(151)
RAM9 = const(152)
RAM10 = const(153)
RAM11 = const(154)
RAM12 = const(155)
RAM13 = const(156)
RAM14 = const(157)
RAM15 = const(158)
RAM16 = const(159)

class DigitSegments:
	def __init__( self, owner, digit_idx, ram_idx ):
		""" owner is the VFD_M6604 class """
		assert RAM1 <= ram_idx <= RAM16
		self.owner = owner
		self.digit_idx = digit_idx
		self.ram_idx = ram_idx
		self.clear()

	def clear( self ):
		self.data = [ 0b11111100, self.ram_idx-RAM1, 0b0, 0b0, 0b0, 0b0, 0b0 ]

	def set( self, seg, value ):
		assert 0 <= seg <= 34, "seg must be from 0 to 34"
		bit_shift = 7-((seg) // 5) # 7..0
		byte_index = 2+(seg % 5)   # 2..6 (0 & 1 are reserved)

		_d = self.data[ byte_index ]
		if value: # Set the bit
			_d |= 1<<bit_shift
		else: # clear the bit
			_d &= (0xFF ^ (1<<bit_shit))
		# Store the updated data
		self.data[ byte_index ] = _d

	def update( self ):
		""" Update the LCD @ char_index """
		self.owner.send_cmd( self.data ) # Store display flags in the related RAM index
		self.owner.display_digit( self.digit_idx, False ) # Not auto-increment
		self.owner.send( bytes([self.ram_idx]) ) # display the RAM idx character

class VFD_M6604():
	""" M6604 Vaccum Fluorescent Display driver """
	def __init__( self, sck, sdata, cs, reset=None ):
		self.sck = sck
		self.sdata = sdata
		self.cs = cs
		self.reset = reset

		self.cs.value( True ) # disable
		if self.reset != None:
			self.reset.value( False ) # Do reset
			time.sleep_ms( 10 )
			self.reset.value( True ) 
			time.sleep_ms( 10 )

	def send( self, arr ):
		# bit banging send of bytes/byteArray content (bit-banging)
		self.cs.value( 0 ) # Active Low
		for data in arr:
			for i in range( 7, -1, -1 ): # MS
				self.sck.value( 0 )
				mask = 1<<i
				self.sdata.value( (data & mask)==mask ) # set state of bit
				time.sleep_ms( 1 )
				self.sck.value( 1 ) # rising edge for data acquisition
				time.sleep_ms( 1 )
		self.cs.value( 1 )

	def send_cmd( self, val_or_list ):
		# convert the given value or a list of value to bytes and send it to the lcd
		if type(val_or_list) is list:
			self.send( bytes(val_or_list) )
		else:
			self.send( bytes([val_or_list]) )


	def cmd_all_digit( self, state ):
		""" return the byte with the command value. state value are True=ALL_ON, False=ALL_OFF, None=normal operation """
		if state == None:
			return 0b11110001
		elif state:
			return 0b11110011
		else:
			return 0b11110000

	def cmd_digit_len( self, value ):
		assert 9<=value<=16
		return 0b00000000 | (value-9)

	def cmd_dimmer( self, value ):
		assert 0<= value <= 7
		return 0b00001 | value

	# Commands

	def all_digit_on( self ):
		""" Set all digit ON (for debugging purpose) """
		self.send_cmd( self.cmd_all_digit(True) )

	def all_digit_off( self ):
		""" Set all digit OFF (for debugging purpose) """
		self.send_cmd( self.cmd_all_digit(False) )

	def normal_operation( self ):
		""" return to normal operation after a all_digit( xxxx ) call """
		self.send_cmd( self.cmd_all_digit(None) )

	def digit_length( self, value ):
		""" Length of display in digits (used by auto incrementation) """
		self.send_cmd( self.cmd_digit_len(value) )


	def dimmer( self, value ):
		""" Dimmer for 0 to 7 """
		self.send_cmd( self.cmd_dimmer(value) )

	def display_freq( self, value ):
		""" One-digit display frequency (Tdsp). 1=256/fOSC, 0=128/fOSC """
		assert value in (0,1)
		self.send_cmd( 0b1111011 | value )

	def display_digit( self, position, auto_incr=False ):
		""" Position from 1..Nth. """
		assert position>=1
		self.send_cmd( [0b11100000 | (position-1), 0b11110100 | (1 if auto_incr else 0)] )

	def define_char( self, ram_idx, char_def ):
		""" Define a 5 x 7 character in RAM char. char_idx is a RAMx constant.
		    char_def is a list define 7 lines of 5 bit wide each.
		    [ 0b00000, 0b01010, 0b10101, 0b10001, 0b01010, 0b00100, 0b00000 ]  """
		assert RAM1 <= ram_idx <= RAM16
		assert (type(char_def) is list) and (len(char_def)==7), "char_def list must have 7 items of 5bits each"
		_data = [ 0b11111100, ram_idx-RAM1 ]
		for bit_shift in range(4,-1,-1): # 4..0
			_val = 0
			bit_mask = 1 << bit_shift
			for row in range(7):
				_val = _val + (1 if (char_def[row] & bit_mask)==bit_mask else 0)
				
				_val = _val << 1 # Bit 0 is not relevant
			_data.append( _val )
		self.send_cmd( _data )

	def attach_digit( self, digit_idx, ram_idx ):
		""" create a DigiSegments instance linked to a Digit position. the segments on/off are controled via the ram_idx custom characters """
		assert 0<=digit_idx<=16
		assert RAM1 <= ram_idx <= RAM16
		_segments = DigitSegments( self, digit_idx, ram_idx )
		_segments.clear()
		return _segments
