#!/usr/bin/python3

from units.shifter import Shifter

from amaranth import *
from amaranth.sim import *

from amaranth.lib.enum import Enum

dut = Shifter()

class ShiftFlag(Enum, shape=unsigned(1)):
    """Shift flag"""
    LEFT=0
    RIGHT = 1

async def shifter_testbench(ctx):
    cases = [
        # direction,     sign-extend    shift amount    x_src1      m_result
        (ShiftFlag.LEFT,  0,            1,              0x00000001, 0x00000002),
        (ShiftFlag.RIGHT, 0,            2,              0x00000008, 0x00000002),
        (ShiftFlag.LEFT,  1,            3,              0xffff1234, 0xfff891a0),
        (ShiftFlag.RIGHT, 1,            4,              0xffff1234, 0xfffff123),
    ]

    for direction, sext, shamt, src, exp in cases:
        ctx.set(dut.x_direction, direction)
        ctx.set(dut.x_sext, sext)
        ctx.set(dut.x_shamt, shamt)
        ctx.set(dut.x_src1, src)
        ctx.set(dut.x_ready, 1)
        await ctx.tick()
        result = ctx.get(dut.m_result)
        assert result == exp, f"Failed: {src:08x} { direction } { shamt } = {result:08x}, expected {exp:08x}"

if __name__ == "__main__":
    sim = Simulator(dut)
    sim.add_clock(Period(MHz=1))
    sim.add_testbench(shifter_testbench)
    with sim.write_vcd("Adder.vcd"):
        sim.run()
