#!/usr/bin/python3

from units.adder import Adder
from units.compare import CompareUnit

from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out

from amaranth.sim import *

from isa import Funct3

class AdderCompareDut(wiring.Component):
    op:        In(3)
    x_src1:    In(32)
    x_src2:    In(32)
    condition: Out(1)

    def elaborate(self, platform):
        m = Module()

        m.submodules.adder = adder = Adder()
        m.submodules.compare = compare = CompareUnit()

        m.d.comb += [
            adder.d_ready.eq(1),
            adder.d_sub.eq(1),    # use sub to compare
            adder.x_src1.eq(self.x_src1),
            adder.x_src2.eq(self.x_src2),
            compare.zero.eq(self.x_src1 == self.x_src2),
            compare.negative.eq(adder.x_result[-1]),
            compare.overflow.eq(adder.x_overflow),
            compare.carry.eq(adder.x_carry),
            compare.op.eq(self.op),
            self.condition.eq(compare.condition_met)
        ]

        return m

dut = AdderCompareDut()

async def compare_testbench(ctx):
    cases = [
        (Funct3.BEQ,  0x7fffffff, 0x7fffffff, True), # ==
        (Funct3.BNE,  0x7fffffff, 0x80000000, True), # !=
        (Funct3.BLT,  0xffffffff, 0x00000002, True), # < (signed)
        (Funct3.BGE,  0xffffffff, 0xfffffffe, True), # > (signed)
        (Funct3.BLTU, 0x12345678, 0x12345679, True), # < (unsigned)
        (Funct3.BGEU, 0x12345679, 0x12345678, True), # > (unsigned)
    ]

    for op, a, b, exp in cases:
        ctx.set(dut.op, op)
        ctx.set(dut.x_src1, a)
        ctx.set(dut.x_src2, b)
        await ctx.tick()
        result = ctx.get(dut.condition)
        assert result == exp, f"Failed: {a:08x} { op } {b:08x} = {result:08x}, expected {exp:08x}"

if __name__ == "__main__":
    sim = Simulator(dut)
    sim.add_clock(Period(MHz=1))
    sim.add_testbench(compare_testbench)
    with sim.write_vcd("CompareUnit.vcd"):
        sim.run()
