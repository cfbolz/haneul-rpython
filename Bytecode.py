from rpython.rlib.rstruct.runpack import runpack


def signed_bytes_to_int(data):
  encoded = str(data).encode('hex')
  return int(encoded, 16)


class BytecodeParser:
  def __init__(self, code):
    self.code = code
    self.pos = 0

  def consume_raw(self, offset=1):
    consumed = b''

    for i in range(0, offset):
      consumed = consumed + self.code[self.pos]
      print "Consumed : " + str(ord(self.code[self.pos]))
      self.pos += 1

    return consumed

  def consume(self, fmt, offset=1):
    return runpack(">" + fmt, self.consume_raw(offset))

  def integer(self):
    is_bigint = self.consume('B')
    if is_bigint == 0:
      data = self.consume('i', 4)
      return data
    else:
      sign = self.consume('B')
      bytes_count = self.consume('Q', 8)
      data = self.consume_raw(bytes_count)
      value = signed_bytes_to_int(data[::-1])
      return value if sign == 1 else -value

  def double(self):
    base = self.integer()
    exp = self.consume('q', 8)
    return base * 2 ** exp

  def char(self):
    head = self.consume('B')
    head_chr = chr(head)

    if head < 0x80:
      return head_chr
    elif head < 0xe0:
      return (head_chr + self.consume_raw(1)).decode('utf-8')
    elif head < 0xf0:
      return (head_chr + self.consume_raw(2)).decode('utf-8')
    else:
      return (head_chr + self.consume_raw(3)).decode('utf-8')


parser = BytecodeParser(
    b'\xf0\x9f\x90\x9d'
)
print parser.char()
