from amaranth import *
from amaranth.lib.enum import Enum

__all__ = [ "INST_ECALL", "INST_EBREAK", "INST_MRET", "INST_SRET", "INST_URET",
            "INST_NOP", "INST_FENCE", "INST_FENCE_I", "INST_WFT", "INST_RET",
            "Opcode", "Funct3", "Funct7", "HoldFlag"]

INST_ECALL  = 0x00000073
INST_EBREAK = 0x00100073
INST_MRET   = 0x30200073
INST_SRET   = 0x10200073
INST_URET   = 0x00200073

INST_NOP    = 0x00000013
INST_FENCE  = 0x0000000F
INST_FENCE_I= 0x0000100F
INST_WFT    = 0x10500073
INST_RET    = 0x00008067

class Opcode(Enum, shape=unsigned(7)):
    """ 7bits Operate code """
    LOAD   = 0b0000011 # I-type: Load from memory
    OP_IMM = 0b0010011 # I-type: Immediate operate
    AUIPC  = 0b0010111 # U-Type: PC add immediate jump
    STORE  = 0b0100011 # S-type: Store to memory
    OP     = 0b0110011 # R-type: Register operate
    LUI    = 0b0110111 # U-type: load upper immediate
    BRANCH = 0b1100011 # B-type: branch
    JALR   = 0b1100111 # I-type: Jump and link register
    JAL    = 0b1101111 # J-type: Jump and link
    SYSTEM = 0b1110011 # I-type: system

class Funct3(Enum, shape=unsigned(3)):
    " 3bits Function code "

    # I-type ALU Operate -> OP_IMM
    ADDI  = 0b000; SLTI  = 0b010; SLTIU = 0b011
    XORI  = 0b100; ORI   = 0b110; ANDI  = 0b111
    SLLI  = 0b001; SRI   = 0b101

    # R-type ALU Operate -> OP
    ADD_SUB = 0b000; SLL = 0b001; SLT = 0b010
    SLTU    = 0b011; XOR = 0b100; SR  = 0b101
    OR      = 0b110; AND = 0b111

    # Load/Store Operate -> LOAD/STORE
    LB  = 0b000; LH  = 0b001; LW = 0b010
    LBU = 0b100; LHU = 0b101
    SB  = 0b000; SH  = 0b001; SW = 0b010

    # Branch Operate -> BRANCH
    BEQ  = 0b000; BNE  = 0b001
    BLT  = 0b100; BGE  = 0b101
    BLTU = 0b110; BGEU = 0b111

    # CSR Operate
    CSRRW  = 0b001; CSRRS  = 0b010; CSRRC  = 0b011
    CSRRWI = 0b101; CSRRSI = 0b110; CSRRCI = 0b111


class Funct7(Enum, shape=unsigned(7)):
    " 7bits Function code "
    ADD = 0b0000000; SUB = 0b0100000
    SLL = 0b0000000; SLT = 0b0000000; SLTU = 0b0000000
    XOR = 0b0000000; SRL = 0b0000000; SRA  = 0b0100000
    OR  = 0b0000000; AND = 0b0000000

    MUL    = 0b0000001; MULH  = 0b0000001
    MULHSU = 0b0000001; MULHU = 0b0000001
    DIV    = 0b0000001; DIVU  = 0b0000001
    REM    = 0b0000001; REMU  = 0b0000001

class Funct12(Enum, shape=unsigned(12)):
    ECALL  = 0b000000000000
    EBREAK = 0b000000000001
    MRET   = 0b001100000010
    WFI    = 0b000100000101

class HoldFlag(Enum, shape=unsigned(3)):
    """Hold flag"""
    HOLD_NONE=0
    HOLD_PC = 1
    HOLD_IF = 2
    HOLD_ID = 3
