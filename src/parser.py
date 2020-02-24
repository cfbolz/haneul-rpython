# -*- coding: utf-8 -*-
import sys
sys.path.append('/home/suhdonghwi/Documents/util/pypy')

import math
from instruction import *
from constant import *
from interpreter import *
from rpython.rlib.rarithmetic import intmask
from rpython.rlib.rstruct.runpack import runpack


class BytecodeParser:
  def __init__(self, code):
    self.code = str(code)
    self.pos = 0

  def consume_raw(self, offset=1):
    consumed = self.code[self.pos:self.pos + offset]
    self.pos += offset
    return consumed

  def consume_raw_reverse(self, offset=1):
    consumed = ''
    for i in range(self.pos + offset - 1, intmask(self.pos) - 1, -1):
      consumed += self.code[i]

    self.pos += offset
    return consumed

  def consume_ubyte(self):
    return runpack(">B", self.consume_raw(1))

  def consume_byte(self):
    return runpack(">b", self.consume_raw(1))

  def consume_ushort(self):
    return runpack(">H", self.consume_raw(2))

  def consume_int(self):
    return runpack(">i", self.consume_raw(4))

  def consume_uint(self):
    return runpack(">I", self.consume_raw(4))

  def consume_longlong(self):
    return runpack(">q", self.consume_raw(8))

  def consume_ulonglong(self):
    return runpack(">Q", self.consume_raw(8))

  def consume_double(self):
    return runpack(">d", self.consume_raw(8))

  def parse_integer(self):
    data = self.consume_longlong()
    return ConstInteger(data)

  def parse_double(self):
    data = self.consume_double()
    return ConstDouble(data)

  def parse_char(self):
    head = self.consume_ubyte()
    result = u''

    if head < 0x80:
      result = unichr(head)
    elif head < 0xe0:
      result = (chr(head) + self.consume_raw(1)).decode('utf-8')
    elif head < 0xf0:
      result = (chr(head) + self.consume_raw(2)).decode('utf-8')
    else:
      result = (chr(head) + self.consume_raw(3)).decode('utf-8')

    return ConstChar(result)

  def parse_string(self):
    count = self.consume_ulonglong()

    result = u''
    for i in range(count):
      result += self.parse_char().charval

    return result

  def parse_string_ubyte(self):
    count = self.consume_ubyte()

    result = u''
    for i in range(count):
      result += self.parse_char().charval

    return result

  def parse_boolean(self):
    value = self.consume_ubyte()
    return ConstBoolean(value == 1)

  def parse_instruction(self):
    line_number = self.consume_uint()
    opcode = self.consume_ubyte()

    inst = Instruction(line_number, opcode)
    if opcode in (INST_PUSH, INST_LOAD, INST_LOAD_DEREF, INST_STORE_GLOBAL, INST_LOAD_GLOBAL):
      inst.operand_int = self.consume_uint()
    elif opcode in (INST_FREE_VAR_LOCAL, INST_FREE_VAR_FREE):
      inst.operand_int = self.consume_ubyte()
    elif opcode == INST_CALL:
      inst.operand_str = self.parse_josa_list()

    return inst

  def parse_constant_list(self):
    count = self.consume_ulonglong()

    result = []
    for i in range(count):
      const_type = self.consume_ubyte()

      if const_type == TYPE_NONE:
        result.append(ConstNone())
      elif const_type == TYPE_INTEGER:
        result.append(self.parse_integer())
      elif const_type == TYPE_REAL:
        result.append(self.parse_double())
      elif const_type == TYPE_CHAR:
        result.append(self.parse_char())
      elif const_type == TYPE_BOOLEAN:
        result.append(self.parse_boolean())
      elif const_type == TYPE_FUNC:
        result.append(self.parse_funcobject())

    return result

  def parse_instruction_list(self):
    count = self.consume_ulonglong()

    result = []
    for i in range(0, count):
      result.append(self.parse_instruction())

    return result

  def parse_string_list(self):
    count = self.consume_ulonglong()

    result = []
    for i in range(0, count):
      result.append(self.parse_string())

    return result

  def parse_josa_list(self):
    count = self.consume_ubyte()

    result = []
    for i in range(0, count):
      result.append(self.parse_string_ubyte())

    return result

  def parse_funcobject(self):
    josa_list = self.parse_josa_list()
    const_table = self.parse_constant_list()
    insts = self.parse_instruction_list()

    return ConstFunc(josa_list, FuncObject(insts, const_table))

  def parse_code(self):
    global_var_names = self.parse_string_list()
    const_table = self.parse_constant_list()
    code = self.parse_instruction_list()

    return (global_var_names, const_table, code)


if __name__ == "__main__":
  parser = BytecodeParser(
      b'\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x04\xeb\xb3\xb4\xec\x97\xac\xec\xa3\xbc\xeb\x8b\xa4\x00\x00\x00\x00\x00\x00\x00\x0a\xed\x94\xbc\xeb\xb3\xb4\xeb\x82\x98\xec\xb9\x98\x20\xec\x88\x98\x20\xea\xb5\xac\xed\x95\x98\xeb\x8b\xa4\x00\x00\x00\x00\x00\x00\x00\x02\x05\x01\x02\xeb\xb2\x88\xec\xa7\xb8\x00\x00\x00\x00\x00\x00\x00\x02\x01\x00\x00\x00\x00\x00\x00\x00\x02\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x11\x00\x00\x00\x02\x02\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x02\x11\x00\x00\x00\x02\x08\x00\x00\x00\x06\x00\x00\x00\x02\x02\x00\x00\x00\x00\x00\x00\x00\x02\x07\x00\x00\x00\x11\x00\x00\x00\x03\x02\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x01\x00\x00\x00\x03\x0c\x00\x00\x00\x03\x05\x00\x00\x00\x01\x00\x00\x00\x03\x06\x01\x02\xeb\xb2\x88\xec\xa7\xb8\x00\x00\x00\x03\x02\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x03\x0c\x00\x00\x00\x03\x05\x00\x00\x00\x01\x00\x00\x00\x03\x06\x01\x02\xeb\xb2\x88\xec\xa7\xb8\x00\x00\x00\x03\x0b\x01\x00\x00\x00\x00\x00\x00\x00\x1e\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x04\x00\x00\x00\x01\x00\x00\x00\x05\x00\x00\x00\x00\x01\x00\x00\x00\x05\x05\x00\x00\x00\x01\x00\x00\x00\x05\x06\x01\x02\xeb\xb2\x88\xec\xa7\xb8\x00\x00\x00\x05\x05\x00\x00\x00\x00\x00\x00\x00\x05\x06\x01\x01\x5f\x00\x00\x00\x05\x01'
  )
  result = parser.parse_code()
  print result

  # def print_builtin_func(args):
  #   print args[0].show().encode('utf-8')
  #   return ConstNone()

  # print_builtin = ConstBuiltin(BuiltinObject(1, print_builtin_func))
  # default_globals = []

  # program = Program(const_table, default_globals)
  # try:
  #   run_code(program, code)
  # except HaneulError as e:
  #   print (u"%d번째 라인에서 에러 발생 : %s" % (e.error_line, e.message)).encode('utf-8')
