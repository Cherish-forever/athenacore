#!/usr/bin/python3

from units.logic import LogicUnit
from amaranth.sim import *
from isa import Funct3

dut = LogicUnit()

async def logic_testbench(ctx):
    cases = [
        # op         src1        src2        result
        (Funct3.XOR, 0xffffffff, 0x00000000, 0xffffffff),
        (Funct3.OR,  0x80000000, 0x00000001, 0x80000001),
        (Funct3.AND, 0x12345678, 0x12345678, 0x12345678),
    ]

    for op, a, b, exp in cases:
        ctx.set(dut.op, op)
        ctx.set(dut.src1, a)
        ctx.set(dut.src2, b)
        result = ctx.get(dut.result)
        assert result == exp, f"Failed: {a:08x} { op } {b:08x} = {result:08x}, expected {exp:08x}"

if __name__ == "__main__":
    sim = Simulator(dut)
    sim.add_testbench(logic_testbench)
    with sim.write_vcd("Adder.vcd"):
        sim.run()
