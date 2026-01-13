#!/usr/bin/python3

from units.adder import Adder
from amaranth.sim import *

dut = Adder()

async def adder_testbench(ctx):
    cases = [
        # x_src1     x_src2      d_sub  x_result
        (0x7fffffff, 0x00000001, False, 0x80000000),
        (0x80000000, 0x00000001, True,  0x7fffffff),
        (0x00000000, 0x00000000, False, 0x00000000),
        (0xffffffff, 0x00000001, False, 0x00000000),
    ]

    for a, b, is_sub, exp in cases:
        ctx.set(dut.x_src1, a)
        ctx.set(dut.x_src2, b)
        ctx.set(dut.d_ready, 1)
        ctx.set(dut.d_sub, is_sub)
        await ctx.tick()
        result = ctx.get(dut.x_result)
        assert result == exp, f"Failed: {a:08x} {'-' if is_sub else '+'} {b:08x} = {result:08x}, expected {exp:08x}"

if __name__ == "__main__":
    sim = Simulator(dut)
    sim.add_clock(Period(MHz=1))
    sim.add_testbench(adder_testbench)
    with sim.write_vcd("Adder.vcd"):
        sim.run()
