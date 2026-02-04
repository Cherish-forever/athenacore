from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out

__all__ = ["BranchPredictor"]

# Usage:
#  Branch: bimm12.eq(Cat(0, insn[8:12], insn[25:31], insn[7], insn[31])),
#     31    30-25      24-20  19-15  14-12    11-8      7        6-0
#  imm[12]  imm[10:5]   rs2    rs1   funct3   imm[4:1]  imm[11]  opcode
#
#  Jump: jimm20.eq(Cat(0, insn[21:31], insn[20], insn[12:20], insn[31])),
#     31    30-21        20        19-12      11-7    6-0
#  imm[20]  imm[10:1]   imm[11]   imm[19:12]   rd    opcode
#
#  funct3:
#         000: beq    001: bneq    100: blt
#         101: bge    110: bltu    111: bgeu
#
#        m.d.comb += [
#            self._predict.d_branch.eq(self._decoder.branch),     # Opcode.BRANCH = 0b11000
#            self._predict.d_jump  .eq(self._decoder.jump),       # Opcode.JAL or Opcode.JALR
#            self._predict.d_offset.eq(self._decoder.immediate),  # bimm12 or jimm20 with signed
#            self._predict.d_pc    .eq(self._d.sink.p.pc),        # pc
#            self._predict.d_rs1_re.eq(self._decoder.rs1_re)      # Branch
#        ]

class BranchPredictor(wiring.Componment):
    d_branch:        In(1)
    d_jump:          In(1)
    d_offset:        In(signed(32))
    d_pc:            In(32)
    d_rs1_re:        In(1)
    d_branch_taken:  Out(1)
    d_branch_target: Out(32)

    def elaborate(self, platform):
        m = Moudle()

        d_fetch_misaligned = Signal() # Is the instruction aligned
        m.d.comb += [
            d_fetch_misaligned.eq(self.d_pc[:2].bool() | self.d_offset[:2].bool()),
            self.d_branch_target.eq(self.d_pc + self.d_offset) # branch target
        ]

        with m.If(d_fetch_misaligned):
            m.d.comb += self.d_branch_taken.eq(0) # not aligned, do not jump
        with m.Elif(self.d_branch):
            # Backward conditional branches are predicted as taken.
            # Forward conditional branches are predicted as not taken.
            m.d.comb += self.d_branch_taken.eq(self.d_offset[-1])
        with m.Else():
            # Direct jumps are predicted as taken.
            # Other branch types (ie. indirect jumps, exceptions) are not predicted.
            m.d.comb += self.d_branch_taken.eq(self.d_jump & ~self.d_rs1_re)

        return m

# Branch:
# in for or while loop
# address instruction
# 0x1000: li x1, 10
# 0x1004: li x2, 0
# 0x1008: loop: add x2, x2, x1
# 0x100C:       addi x1, x1, -1
# 0x1010:       bnez x1, loop # the offset always < 0
#
# 10 times d_branch_taken is right, but 11 times is wrong

# Jump:
# if current instruction is type Jump not Branch, it need d_branch_taken
