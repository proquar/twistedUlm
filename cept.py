#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
#    Character-Definitions in this file are taken from:
#
#    Bildschirmtricks MikroPAD V2.0.0  btx service control
#    Copyright (C) 2008 Philipp Fabian Benedikt Maier (aka. Dexter)
#
#
#
#    Copyright (C) 2009 by Christian Groeger
#    christian@proquariat.de
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.



CHARS = {
	'sp':0x20,
	'apb':0x08,				# active position back
	'apf':0x09,				# active position forward
	'apd':0x0a,				# active position down
	'apu':0x0b,				# active position up
	'cs':0x0c,				# clear screen
	'apr':0x0d,				# active position return
	'si':0x0e, 				# shift in
	'so':0x0f, 				# shift out
	'con':0x11,				# cursor on
	'rpt':0x12,				# repeat last character
	'cof':0x14,				# cursor off
	'can':0x18,				# cancel (fills the rest off the line with spaces)
	'ss2':0x19,				# single shift 2 (g2 set, some legents say that this is the magic "yes" character)
	'esc':0x1b,				# escape
	'ss3':0x1d,				# single shift 3 (g3 set)
	'aph':0x1e,				# active position home
	'us':0x1f,				# unit seperator (also known as apa)
	
	# c0 data link control tokens (single byte constants)
	'nul':0x00,				# null
	'soh':0x01,				# start of heading
	'stx':0x02,				# start text
	'etx':0x03,				# end text
	'eot':0x04,				# end of transmission
	'enq':0x05,				# enquiry
	'ack':0x06,				# acknowledge
	'itb':0x07,				# end intermediate block
	'dle':0x10,				# data link escape
	'nak':0x15,				# negative acknowledge
	'syn':0x16,				# syncronize
	'etb':0x17,				# end textblock
	# note: the data link control tokens are not mentiond in ets_300_072
	
	# c0 propritay-btx tokens (single byte constants)
	'ini':0x13,				# initiator (*)
	'ter':0x1c,				# terminator (#)
	'dct':0x1a,				# propritary btx (makes the terminal talking)
	
	# c1s/c1p control functions set (single byte constants)
	'fsh':0x88,				# flash
	'std':0x89,				# steady
	'ebx':0x8a,				# end box
	'sbx':0x8b,				# start box
	'nsz':0x8c,				# normal-size
	'dbh':0x8d,				# double-height
	'dbw':0x8e,				# double-width
	'dbs':0x8f,				# double-size
	'cdy':0x98,				# conceal display
	'spl':0x99,				# stop lining
	'stl':0x9a,				# start lining
	'csi':0x9b,				# control sequence introducer
	
	# c1s control functions set (single byte constants)
	'abk':0x80,				# alpha black
	'anr':0x81,				# alpha red
	'ang':0x82,				# alpha green
	'any':0x83,				# alpha yellow
	'anb':0x84,				# alpha blue
	'anm':0x85,				# alpha mageta
	'anc':0x86,				# alpha cyan
	'anw':0x87,				# alpha white
	'mbk':0x90,				# mosaic black
	'msr':0x91,				# mosaic red
	'msg':0x92,				# mosaic green
	'msy':0x93,				# mosaic yellow
	'msb':0x94,				# mosaic blue
	'msm':0x95,				# mosaic magenta
	'msc':0x96,				# mosaic cyan
	'msw':0x97,				# mosaic white
	'bbd':0x9c,				# black background
	'nbd':0x9d,				# new background
	'hms':0x9e,				# hold mosaic
	'rms':0x9f,				# release mosaic
	
	# c1p control functions set (single byte constants)
	'bkf':0x80,				# black foreground
	'rdf':0x81,				# red foreground
	'grf':0x82,				# green foreground
	'ylf':0x83,				# yellow foreground
	'blf':0x84,				# blue foreground
	'mgf':0x85,				# magenta foreground
	'cnf':0x86,				# cyan foreground
	'whf':0x87,				# white foreground
	'bkb':0x90,				# black background
	'rdb':0x91,				# red background
	'grb':0x92,				# green background
	'ylb':0x93,				# yellow background
	'blb':0x94,				# blue background
	'mgb':0x95,				# magenta background
	'cnb':0x96,				# cyan background
	'whb':0x97,				# white background
	'npo':0x9c,				# normal polarity
	'ipo':0x9d,				# inverted polarity
	'trb':0x9e,				# transparent background
	'stc':0x9f,				# stop conceal
	
	# fe full screen atributes (single byte constants)
	'fbkb':0x50,				# black background
	'frdb':0x51,				# red background
	'fgrb':0x52,				# green background
	'fylb':0x53,				# yellow background
	'fblb':0x54,				# blue background
	'fmgb':0x55,				# magenta background
	'fcnb':0x56,				# cyan background
	'fwhb':0x57,				# white background
	'ftrb':0x5e				# transparent background
	}
