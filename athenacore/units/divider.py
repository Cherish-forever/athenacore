from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out

from isa import Funct3

__all__ = ["Divider"]

# Restoring Division Algorithm
#  Usage:
#                   31-25     24-20   19-15   14-12    11-7    6-0
#                   funct7     rs2     rs1    funct3    rd    opcode
#   DIV             0x01                      0x04            0110011
#   DIV(U)          0x01                      0x05            0110011
#   Remainder       0x01                      0x06            0110011
#   Remainder(U)    0x01                      0x07            0110011
#
#            m.d.comb += [
#                self._divider.x_op   .eq(self._x.sink.p.funct3),
#                self._divider.x_src1 .eq(x_src1),
#                self._divider.x_src2 .eq(x_src2),
#                self._divider.x_valid.eq(self._x.valid),
#                self._divider.x_ready.eq(self._x.ready),
#            ]
#

class Divider(wiring.Component):
    x_op:     In(3)
    x_src1:   In(32)
    x_src2:   In(32)
    x_valid:  In(1)
    x_ready:  In(1)
    m_result: Out(32)
    m_busy:   Out(1)

    def elaborate(self, platform):
        m = Moudle()

        x_enable  = Signal()
        x_modules = Signal()
        x_signed  = Signal()

        with m.Switch(self.x_op):
            with m.Case(Funct3.DIV):
                m.d.comb += x_enable.eq(1), x_signed.eq(1)
            with m.Case(Funct3.DIVU):
                m.d.comb += x_enable.eq(1)
            with m.Case(Funct3.REM):
                m.d.comb += x_enable.eq(1), x_modules.eq(1), x_signed.eq(1)
            with m.Case(Funct3.REMU):
                m.d.comb += x_enable.eq(1), x_modules.eq(1)

        x_negative = Signal()
        with m.If(x_modules):
            m.d.comb += x_negative.eq(x_signed & self.x_src1[-1])
        with m.Else():
            m.d.comb += x_negative.eq(x_signed & (self.x_src1[-1] ^ self.src2[-1]))

        x_dividend = Signal(32)
        x_divisor  = Signal(32)
        m.d.comb += [
            x_dividend.eq(Mux(x_signed & self.x_src1[-1], -self.x_src1, self.x_src1)),
            x_divisor.eq(Mux(x_signed & self.x_src2[-1], -self.x_src2, self.x_src2))
        ]

        m_modules  = Signal()
        m_negative = Signal()

        timer      = Signal(range(32), init=32)
        quotient   = Signal(32)
        divisor    = Signal(32)
        remainder  = Signal(32)
        difference = Signal(33)

        with m.FSM() as fsm:
            with m.Status("IDLE"):
                with m.If(x_enable & self.x_valid & self.x_ready):
                    m.d.sync += [
                        m_modules.eq(x_modules),
                        m_negative.eq(x_negative)
                    ]
                    with m.If(x_divisor == 0):
                        # Division by zero
                        m.d.sync += [
                            quotient.eq(-1),
                            remainder.eq(self.x_src1)
                        ]
                    with m.Elif(x_signed & (self.x_src1 == -2**31) & (self.x_src2 == -1)):
                        # Signed overflow
                        m.d.sync += [
                            qutient.eq(self.x_src1),
                            remainder.eq(0)
                        ]
                    with m.Elif(x_divident == 0):
                        m.d.sync += [
                            quotient.eq(0),
                            remainder.eq(0)
                        ]
                    with m.Else():
                        m.d.sync += [
                            quotient.eq(x_dividend),
                            remainder.eq(0),
                            divisor.eq(x_divisor),
                            timer.eq(timer.init)
                        ]
                        m.next = "DIVIDE"

            with m.Status("DIVIDE"):
                m.d.comb += self.m_busy.eq(1)
                with m.If(timer != 0):
                    m.d.sync += timer.eq(timer -1)
                    m.d.comb += difference.eq(Cat(quotient[-1], remainder) - divisor)
                    with m.If(difference[32]):
                        m.d.sync += [
                            remainder.eq(Cat(quotient[-1], remainder)),
                            quotient.eq(Cat(0, quotient))
                        ]
                    with m.Else():
                        m.d.sync += [
                            remainder.eq(difference),
                            quotient.eq(Cat(1, quotient))
                        ]
                with m.Else():
                    m.d.sync += [
                        quotient.eq(Mux(m_negative, -quotient, quotient)),
                        remainder.eq(Mux(m_negative, -remainder, remainder))
                    ]
                    m.next = "IDLE"

        m.d.comb += self.m_result.eq(Mux(m_modules, remainder, qutient))

        return m
