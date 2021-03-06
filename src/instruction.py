instructions = ['PUSH', 'POP', 'LOAD', 'LOAD_DEREF', 'STORE_GLOBAL', 'LOAD_GLOBAL',
                'CALL', 'JMP', 'POP_JMP_IF_FALSE', 'FREE_VAR_LOCAL', 'FREE_VAR_FREE',
                'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'MOD', 'EQUAL', 'LESS_THAN', 'GREATER_THAN', 'NEGATE']
for (i, inst) in enumerate(instructions):
  globals()['INST_' + inst] = i


class Instruction:
  _immutable_fields_ = ['line_number',
                        'opcode', 'operand_int', 'operand_str[*]']

  def __init__(self, line_number, opcode):
    self.line_number = line_number
    self.opcode = opcode
    self.operand_int = 0
    self.operand_str = [u'']
