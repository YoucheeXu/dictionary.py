#!/usr/bin/python3
#-*- encoding:utf-8 -*-
# -*- coding: utf-8 -*-
#coding=utf-8
'''
V1.0 only support single mdx
'''
import tempfile
import re
import struct
from io import BytesIO
# zlib compression is used for engine version >=2.0
import zlib

# pip install python3-lzo-indexer
# pip install python-lzo
# LZO compression is used for engine version < 2.0
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-lzo
try:
	import lzo
except ImportError:
	lzo = None
	print("LZO compression support is not available")

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from src.ripemd128 import ripemd128
from src.puresalsa20 import Salsa20
from src.dictbase import DictBase
from src.globalvar import GetLogger

# def _unescape_entities(text):
	# """
	# unescape offending tags < > " &
	# """
	# text = text.replace(b'&lt;', b'<')
	# text = text.replace(b'&gt;', b'>')
	# text = text.replace(b'&quot;', b'"')
	# text = text.replace(b'&amp;', b'&')
	# return text


class MDictBase(DictBase):
	""" read from mdd, mdx
	"""

	def __init__(self, dictSrc, isMdd = False, password = None):
		global gLogger

		gLogger = GetLogger()

		self.__TempDir = tempfile.gettempdir()
		self.__DictPackage = dictSrc

		if isMdd:
			self.__Encoding = 'UTF-16'
		else:
			self.__Encoding = ""

		self.__Substyle = False

		self.__Password = password

		self.__HeaderTag = self.__ReadHead()

		self.__WordDict = {}

		# self.__KeyDict = self.__ReadKeys()
		# gLogger.info("Key Dict = %s" %str(self.__KeyDict))
		self.__KeyList = self.__ReadKeys()
		# gLogger.info(self.__KeyDict)
		# self.__WordList = self.__KeyDict.keys()

		if isMdd:
			self.__DecodeMddRecordBlock()
		else:
			self.__DecodeMdxRecordBlock()

		# gLogger.info(self.__WordDict)
		self.__WordList = self.__WordDict.keys()
		# print(self.__WordList)

	def close(self):
		pass

	def __ReadHead(self):
		# global gLogger

		with open(self.__DictPackage, "rb") as f:
			# number of bytes of header text, big-endian, integer
			header_bytes_size = struct.unpack(">I", f.read(4))[0]
			# print(header_bytes_size)
			header_bytes = f.read(header_bytes_size)
			# 4 bytes: adler32 checksum of header, in little endian
			adler32 = struct.unpack('<I', f.read(4))[0]
			# print(adler32)
			assert(adler32 == zlib.adler32(header_bytes) & 0xffffffff)
			# mark down key block offset
			self.__KeyBlockOffset = f.tell()

		# header text in utf-16 encoding ending with '\x00\x00'
		# header_text = header_bytes[:-2].decode('utf-16').encode('utf-8')
		header_text = header_bytes[:-2].decode('utf-16')
		# gLogger.info(header_text)
		header_tag = self.__Parse_header(header_text)
		gLogger.info(header_tag)
		# print(header_tag.getAttribute("Encoding"))
		if not self.__Encoding:
			encoding = header_tag['Encoding']
			# print(encoding)
			# if sys.hexversion >= 0x03000000:
				# encoding = encoding.decode('utf-8')
			# GB18030 > GBK > GB2312
			if encoding in ['GBK', 'GB2312']:
				encoding = 'GB18030'
			self.__Encoding = encoding
		gLogger.info("encoding = %s" %self.__Encoding)
		# encryption flag
		#   0x00 - no encryption
		#   0x01 - encrypt record block
		#   0x02 - encrypt key info block
		if 'Encrypted' not in header_tag or header_tag['Encrypted'] == 'No':
			self.__Encrypt = 0
		elif header_tag['Encrypted'] == 'Yes':
			self.__Encrypt = 1
		else:
			self.__Encrypt = int(header_tag['Encrypted'])
		gLogger.info("Encrypted = %d" %self.__Encrypt)
		# stylesheet attribute if present takes form of:
		#   style_number # 1-255
		#   style_begin  # or ''
		#   style_end	# or ''
		# store stylesheet in dict in the form of
		# {'number' : ('style_begin', 'style_end')}
		self.__Stylesheet = {}
		if header_tag.get('StyleSheet'):
			lines = header_tag['StyleSheet'].splitlines()
			for i in range(0, len(lines), 3):
				self.__Stylesheet[lines[i]] = (lines[i+1], lines[i+2])
			self.__Substyle = True
		else:
			self.__Substyle = False

		gLogger.info("stylesheet = " + str(self.__Stylesheet))
		# before version 2.0, number is 4 bytes integer
		# version 2.0 and above uses 8 bytes
		self.__Version = float(header_tag['GeneratedByEngineVersion'])
		gLogger.info("version = %f" %self.__Version)
		if self.__Version < 2.0:
			self.__NumberWidth = 4
			self.__NumberFormat = '>I'
		else:
			self.__NumberWidth = 8
			self.__NumberFormat = '>Q'

		return header_tag		

	def __ReadKeys(self):
		# global gLogger

		with open(self.__DictPackage, 'rb') as f:
			f.seek(self.__KeyBlockOffset)

			# the following numbers could be encrypted
			if self.__Version >= 2.0:
				num_bytes = self.__NumberWidth * 5
			else:
				num_bytes = self.__NumberWidth * 4
			block = f.read(num_bytes)

			if self.__Encrypt & 1:
				if self.__Passcode is None:
					raise RuntimeError('user identification is needed to read encrypted file')
				regcode, userid = self.__Passcode
				if isinstance(userid, unicode):
					userid = userid.encode('utf8')
				if self.__HeaderTag['RegisterBy'] == 'EMail':
					encrypted_key = _decrypt_regcode_by_email(regcode, userid)
				else:
					encrypted_key = _decrypt_regcode_by_deviceid(regcode, userid)
				block = _salsa_decrypt(block, encrypted_key)

			# decode this block
			sf = BytesIO(block)
			# number of key blocks
			NumKeyBlocks = self.__ReadNumber(sf)
			gLogger.info("Number of Key Blocks = %d" %NumKeyBlocks)

			# number of entries
			self.__NumEntries = self.__ReadNumber(sf)
			gLogger.info("Number of Entries = %d" %self.__NumEntries)
			
			# number of bytes of key block info after decompression
			if self.__Version >= 2.0:
				# Number of Bytes After Decompression
				KeyBlockInfoDecompSize = self.__ReadNumber(sf)
			# number of bytes of key block info
			KeyBlockInfoSize = self.__ReadNumber(sf)
			# number of bytes of key block
			KeyBlockSize = self.__ReadNumber(sf)

			# 4 bytes: adler checksum of previous 5 numbers
			if self.__Version >= 2.0:
				adler32 = struct.unpack('>I', f.read(4))[0]
				assert adler32 == (zlib.adler32(block) & 0xffffffff)

			# read key block info, which indicates key block's compressed and decompressed size
			KeyBlockInfo = f.read(KeyBlockInfoSize)
			KeyBlockInfoList = self.__DecodeKeyBlockInfo(KeyBlockInfo, KeyBlockInfoDecompSize)
			assert(NumKeyBlocks == len(KeyBlockInfoList))

			# read key block
			KeyBlockCompressed = f.read(KeyBlockSize)
			# extract key block
			KeyList = self.__DecodeKeyBlocks(KeyBlockCompressed, KeyBlockInfoList)

			self.__RecordBlockOffset = f.tell()

		# keyDict = {key.decode(self.__Encoding): value for value, key in KeyList}
		# keyDict = {key: value for value, key in KeyList}
		# return keyDict

		return KeyList

	def __Parse_header(self, header_text):
		"""
		extract attributes from <Dict attr="value" ... >
		"""
		# tagdict = {}

		# taglist = re.findall(b'(\w+)="(.*?)"', header_text, re.DOTALL)
		# for key, value in taglist:
			# tagdict[key] = _unescape_entities(value)

		# DOMTree = xml.dom.minidom.parseString(header_text)
		# print("tagName = ", DOMTree.documentElement.tagName)
		# return DOMTree.documentElement

		root = ET.fromstring(header_text)

		# print(root.tag, ":", root.attrib)

		# return tagdict
		return root.attrib

	def __ReadNumber(self, f):
		return struct.unpack(self.__NumberFormat, f.read(self.__NumberWidth))[0]

	def __DecodeKeyBlockInfo(self, keyBlockInfoCompressed, KeyBlockInfoDecompSize):
		if self.__Version >= 2:
			# zlib compression
			assert(keyBlockInfoCompressed[:4] == b'\x02\x00\x00\x00')
			# decrypt if needed
			if self.__Encrypt & 0x02:
				keyBlockInfoCompressed = self.__MdxDecrypt(keyBlockInfoCompressed)
			# decompress
			keyBlockInfo = zlib.decompress(keyBlockInfoCompressed[8:])
			# adler checksum
			adler32 = struct.unpack('>I', keyBlockInfoCompressed[4:8])[0]
			assert(adler32 == zlib.adler32(keyBlockInfo) & 0xffffffff)
		else:
			# no compression
			keyBlockInfo = keyBlockInfoCompressed
		# decode
		KeyBlockInfoList = []
		numEntries = 0
		i = 0
		if self.__Version >= 2:
			byteFormat = '>H'
			byteWidth = 2
			textTerm = 1
		else:
			byteFormat = '>B'
			byteWidth = 1
			textTerm = 0

		while i < len(keyBlockInfo):
			# number of entries in current key block
			numEntries += struct.unpack(self.__NumberFormat, keyBlockInfo[i:i+self.__NumberWidth])[0]
			i += self.__NumberWidth
			# text head size
			textHeadSize = struct.unpack(byteFormat, keyBlockInfo[i:i+byteWidth])[0]
			i += byteWidth
			# text head
			if self.__Encoding != 'UTF-16':
				i += textHeadSize + textTerm
			else:
				i += (textHeadSize + textTerm) * 2
			# text tail size
			textTailSize = struct.unpack(byteFormat, keyBlockInfo[i:i+byteWidth])[0]
			i += byteWidth
			# text tail
			if self.__Encoding != 'UTF-16':
				i += textTailSize + textTerm
			else:
				i += (textTailSize + textTerm) * 2

			# print(i, self.__NumberFormat, self.__NumberWidth)
			# key block compressed size
			keyBlockCompressedSize = struct.unpack(self.__NumberFormat, keyBlockInfo[i:i+self.__NumberWidth])[0]
			i += self.__NumberWidth
			# key block decompressed size
			keyBlockDecompressedSize = struct.unpack(self.__NumberFormat, keyBlockInfo[i:i+self.__NumberWidth])[0]
			i += self.__NumberWidth
			KeyBlockInfoList += [(keyBlockCompressedSize, keyBlockDecompressedSize)]

		#assert(numEntries == self.__NumEntries)

		return KeyBlockInfoList

	def __FastDecrypt(self, data, key):
		b = bytearray(data)
		key = bytearray(key)
		previous = 0x36
		for i in range(len(b)):
			t = (b[i] >> 4 | b[i] << 4) & 0xff
			t = t ^ previous ^ (i & 0xff) ^ key[i % len(key)]
			previous = b[i]
			b[i] = t
		return bytes(b)

	def __MdxDecrypt(self, compBlock):
		key = ripemd128(compBlock[4:8] + struct.pack(b'<L', 0x3695))
		return compBlock[0:8] + self.__FastDecrypt(compBlock[8:], key)

	def __DecodeKeyBlocks(self, keyBlockCompressed, keyBlockInfoList):
		keyList = []
		i = 0
		for compressedSize, decompressedSize in keyBlockInfoList:
			start = i
			end = i + compressedSize
			# 4 bytes : compression type
			keyBlockType = keyBlockCompressed[start:start+4]
			# 4 bytes : adler checksum of decompressed key block
			adler32 = struct.unpack('>I', keyBlockCompressed[start+4:start+8])[0]
			if keyBlockType == b'\x00\x00\x00\x00':
				keyBlock = keyBlockCompressed[start+8:end]
			elif keyBlockType == b'\x01\x00\x00\x00':
				if lzo is None:
					print("LZO compression is not supported")
					break
				# decompress key block
				header = b'\xf0' + pack('>I', decompressedSize)
				keyBlock = lzo.decompress(header + keyBlockCompressed[start+8:end])
			elif keyBlockType == b'\x02\x00\x00\x00':
				# decompress key block
				keyBlock = zlib.decompress(keyBlockCompressed[start+8:end])
			# extract one single key block into a key list
			keyList += self.__DecodeKeyBlock(keyBlock)
			# notice that adler32 returns signed value
			assert(adler32 == zlib.adler32(keyBlock) & 0xffffffff)

			i += compressedSize
		return keyList

	def __DecodeKeyBlock(self, keyBlock):
		keyList = []
		keyStartIndex = 0
		while keyStartIndex < len(keyBlock):
			# the corresponding record's offset in record block
			keyId = struct.unpack(self.__NumberFormat, keyBlock[keyStartIndex:keyStartIndex+self.__NumberWidth])[0]
			# key text ends with '\x00'
			if self.__Encoding == 'UTF-16':
				delimiter = b'\x00\x00'
				width = 2
			else:
				delimiter = b'\x00'
				width = 1
			i = keyStartIndex + self.__NumberWidth
			while i < len(keyBlock):
				if keyBlock[i:i+width] == delimiter:
					keyEndIndex = i
					break
				i += width
			keyText = keyBlock[keyStartIndex+self.__NumberWidth:keyEndIndex]\
				.decode(self.__Encoding, errors='ignore').encode('utf-8').strip()
			keyStartIndex = keyEndIndex + width
			keyList += [(keyId, keyText)]
		return keyList

	def __DecodeMddRecordBlock(self):
		# global gLogger

		with open(self.__DictPackage, 'rb') as f:
			f.seek(self.__RecordBlockOffset)

			numRecordBlocks = self.__ReadNumber(f)
			numEntries = self.__ReadNumber(f)
			assert(numEntries == self.__NumEntries)
			recordBlockInfoSize = self.__ReadNumber(f)
			recordBlockSize = self.__ReadNumber(f)

			# record block info section
			recordBlockInfoList = []
			sizeCounter = 0
			for i in range(numRecordBlocks):
				compressedSize = self.__ReadNumber(f)
				decompressedSize = self.__ReadNumber(f)
				recordBlockInfoList += [(compressedSize, decompressedSize)]
				sizeCounter += self.__NumberWidth * 2
			assert(sizeCounter == recordBlockInfoSize)

			# actual record block
			offset = 0
			i = 0
			sizeCounter = 0
			for compressedSize, decompressedSize in recordBlockInfoList:
				compressBlockStart = f.tell()
				recordBlockCompressed = f.read(compressedSize)
				# 4 bytes: compression type
				recordBlockType = recordBlockCompressed[:4]
				# 4 bytes: adler32 checksum of decompressed record block
				adler32 = struct.unpack('>I', recordBlockCompressed[4:8])[0]
				if recordBlockType == b'\x00\x00\x00\x00':
					recordBlock = recordBlockCompressed[8:]
				elif recordBlockType == b'\x01\x00\x00\x00':
					if lzo is None:
						print("LZO compression is not supported")
						break
					# decompress
					header = b'\xf0' + struct.pack('>I', decompressedSize)
					recordBlock = lzo.decompress(header + recordBlockCompressed[8:])
				elif recordBlockType == b'\x02\x00\x00\x00':
					# decompress
					recordBlock = zlib.decompress(recordBlockCompressed[8:])

				# notice that adler32 return signed value
				assert(adler32 == zlib.adler32(recordBlock) & 0xffffffff)

				assert(len(recordBlock) == decompressedSize)
				# split record block according to the offset info from key block
				while i < len(self.__KeyList):
					recordStart, keyText = self.__KeyList[i]
					# reach the end of current record block
					if recordStart - offset >= len(recordBlock):
						break
					# record end index
					if i < len(self.__KeyList)-1:
						recordEnd = self.__KeyList[i+1][0]
					else:
						recordEnd = len(recordBlock) + offset
					i += 1

					'''
					data = recordBlock[recordStart-offset: recordEnd-offset]

					# fname = keyText.decode('utf-8').replace('\\', os.path.sep)
					fname = keyText.decode('utf-8').replace('\\', '')
					with open(fname, "wb") as f:
						f.write(data)
					'''

					# yield keyText, data
					info = recordStart-offset, recordEnd-offset, compressBlockStart, compressedSize, decompressedSize
					self.__WordDict.setdefault(keyText.decode("UTF-8"), info)

				offset += len(recordBlock)
				sizeCounter += compressedSize
			assert(sizeCounter == recordBlockSize)

	def __DecodeMdxRecordBlock(self):
		# global gLogger

		with open(self.__DictPackage, 'rb') as f:
			f.seek(self.__RecordBlockOffset)

			numRecordBlocks = self.__ReadNumber(f)
			gLogger.info("Number of Record Blocks = %d" %numRecordBlocks)
			numEntries = self.__ReadNumber(f)
			assert(numEntries == self.__NumEntries)
			recordBlockInfoSize = self.__ReadNumber(f)
			recordBlockSize = self.__ReadNumber(f)

			# record block info section
			recordBlockInfoList = []
			sizeCounter = 0
			for i in range(numRecordBlocks):
				compressedSize = self.__ReadNumber(f)
				decompressedSize = self.__ReadNumber(f)
				recordBlockInfoList += [(compressedSize, decompressedSize)]
				sizeCounter += self.__NumberWidth * 2
			assert(sizeCounter == recordBlockInfoSize)

			# actual record block data
			offset = 0
			i = 0
			sizeCounter = 0
			for compressedSize, decompressedSize in recordBlockInfoList:
				# print(compressedSize, decompressedSize)
				compressBlockStart = f.tell()
				recordBlockCompressed = f.read(compressedSize)
				# 4 bytes indicates block compression type
				recordBlockType = recordBlockCompressed[:4]
				# 4 bytes adler checksum of uncompressed content
				adler32 = struct.unpack('>I', recordBlockCompressed[4:8])[0]
				# no compression
				if recordBlockType == b'\x00\x00\x00\x00':
					recordBlock = recordBlockCompressed[8:]
				# lzo compression
				elif recordBlockType == b'\x01\x00\x00\x00':
					if lzo is None:
						print("LZO compression is not supported")
						break
					# decompress
					header = b'\xf0' + pack('>I', decompressedSize)
					recordBlock = lzo.decompress(header + recordBlockCompressed[8:])
				# zlib compression
				elif recordBlockType == b'\x02\x00\x00\x00':
					# decompress
					recordBlock = zlib.decompress(recordBlockCompressed[8:])

				# notice that adler32 return signed value
				assert(adler32 == zlib.adler32(recordBlock) & 0xffffffff)

				assert(len(recordBlock) == decompressedSize)

				# split record block according to the offset info from key block
				# for word, recordStart in self.__KeyDict.items():
				while i < len(self.__KeyList):
					recordStart, keyText = self.__KeyList[i]
					# reach the end of current record block
					if recordStart - offset >= len(recordBlock):
						break
					# record end index
					if i < len(self.__KeyList)-1:
						recordEnd = self.__KeyList[i+1][0]
					else:
						recordEnd = len(recordBlock) + offset
					i += 1

					'''
					record = recordBlock[recordStart-offset: recordEnd-offset]
					# convert to utf-8
					record = record.decode(self.__Encoding, errors = 'ignore').strip(u'\x00').encode('utf-8')
					# substitute styles
					if self.__Substyle and self.__Stylesheet:
						record = self.__SubstituteStylesheet(record)
					'''

					# yield keyText, record
					# self.__WordDict.update({keyText: record})

					info = recordStart-offset, recordEnd-offset, compressBlockStart, compressedSize, decompressedSize
					self.__WordDict.setdefault(keyText.decode("UTF-8"), info)
					# print(keyText, record)

				offset += len(recordBlock)
				sizeCounter += compressedSize

			assert(sizeCounter == recordBlockSize)

	def __SubstituteStylesheet(self, txt):
		# substitute stylesheet definition
		txt_list = re.split('`\d+`', txt)
		txt_tag = re.findall('`\d+`', txt)
		txt_styled = txt_list[0]
		for j, p in enumerate(txt_list[1:]):
			style = self.__Stylesheet[txt_tag[j][1:-1]]
			if p and p[-1] == '\n':
				txt_styled = txt_styled + style[0] + p.rstrip() + style[1] + '\r\n'
			else:
				txt_styled = txt_styled + style[0] + p + style[1]
		return txt_styled

	def get_parseFun(self):
		return "dictHtml"

	def query_word(self, word):
		if word in self.__WordList:
			RecordStart, RecordEnd, CompressBlockStart, CompressBlcokSize, DecompressSize = self.__WordDict[word]
			with  open(self.__DictPackage, 'rb') as f:
				f.seek(CompressBlockStart)
				recordBlockCompressed = f.read(CompressBlcokSize)
				# 4 bytes indicates block compression type
				recordBlockType = recordBlockCompressed[:4]
				# 4 bytes adler checksum of uncompressed content
				adler32 = struct.unpack('>I', recordBlockCompressed[4:8])[0]
				# no compression
				if recordBlockType == b'\x00\x00\x00\x00':
					recordBlock = recordBlockCompressed[8:]
				# lzo compression
				elif recordBlockType == b'\x01\x00\x00\x00':
					if lzo is None:
						return False, "LZO compression is not supported"
					# decompress
					header = b'\xf0' + pack('>I', DecompressSize)
					recordBlock = lzo.decompress(header + recordBlockCompressed[8:])
				# zlib compression
				elif recordBlockType == b'\x02\x00\x00\x00':
					# decompress
					recordBlock = zlib.decompress(recordBlockCompressed[8:])

				# notice that adler32 return signed value
				assert(adler32 == zlib.adler32(recordBlock) & 0xffffffff)

				assert(len(recordBlock) == DecompressSize)

				record = recordBlock[RecordStart: RecordEnd]
				# convert to utf-8
				record = record.decode(self.__Encoding, errors = 'ignore').strip(u'\x00')
				# substitute styles
				if self.__Substyle and self.__Stylesheet:
					record = self.__SubstituteStylesheet(record)
				return True, record
		else:
			return False, "Word isn't in DictBase."

	def get_wordsLst(self, wdsLst, word):
		wordLike = "^" + word + ".*"
		regex = re.compile(wordLike)
		for word in self.__WordList:
			match = regex.search(word)
			if match:
				wdsLst.append(word)

		if len(wdsLst) >= 1: return True
		else: return False

	def del_word(self, word):
		raise NotImplementedError("don't support to delete word: " + word)
		return False

if __name__ == '__main__':
	pass