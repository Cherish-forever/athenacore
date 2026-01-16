#!/usr/bin/python3

from units.decoder import InstructionDecoder

from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out

from amaranth.sim import *

from isa import Opcode, Funct3, Funct7, Funct12

dut = InstructionDecoder(with_muldiv=True)

async def test_r_type(ctx):
    cases = [
        (0x00b505b3, dict( # add x11, x10, x11
            rd=11, rd_we=1, rs1=10, rs1_we=1, rs2=11, rs2_we=1, funct3=0b000,
            adder=1, adder_sub=0, logic=0, shift=0, immediate=0, illegal=0
        )),
        (0x40b505b3, dict( # sub x11, x21, x22
            rd=11, rd_we=1, rs1=10, rs1_we=1, rs2=11, rs2_we=1, funct3=0b000,
            adder=1, adder_sub=1, logic=0, shift=0, immediate=0, illegal=0
        )),
        (0x00b565b3, dict( # or x11, x21, x22
            rd=11, rd_we=1, rs1=10, rs1_we=1, rs2=11, rs2_we=1, funct3=0b110,
            adder=0, adder_sub=0, logic=1, shift=0, immediate=0, illegal=0
        )),
        (0x00b555b3, dict( # srl x11, x21, x21
            rd=11, rd_we=1, rs1=10, rs1_we=1, rs2=11, rs2_we=1, funct3=0b101,
            adder=0, adder_sub=0, logic=0, shift=1, direction=1, immediate=0, illegal=0
        )),
    ]

    for instr, exp in cases:
        ctx.set(dut.instruction, instr)
        for field, val in exp.items():
            result = ctx.get(getattr(dut, field))
            assert result == val, f"R-type 0x{instr:08x} field {field} result {result} exp {val}"

if __name__ == "__main__":
    sim = Simulator(dut)
    sim.add_testbench(test_r_type)
    with sim.write_vcd("decoder.vcd"):
        sim.run()
