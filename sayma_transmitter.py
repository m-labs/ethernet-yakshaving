#!/usr/bin/env python3

import sys

from migen import *
from migen.genlib.fsm import *
from migen.genlib.cdc import AsyncResetSynchronizer
from migen.build.platforms.sinara import sayma_amc
from migen.genlib.io import DDROutput
from misoc.cores.liteeth_mini.phy.rgmii import LiteEthPHYRGMIITX


class TrafficGenerator(Module):
    def __init__(self, packet, repeat_bits):
        self.stb = Signal()
        self.data = Signal(8)

        repeat = Signal()
        repeat_counter = Signal(repeat_bits)
        self.sync += Cat(repeat_counter, repeat).eq(repeat_counter + 1)

        mem = Memory(8, len(packet), init=packet)
        port = mem.get_port()
        self.specials += mem, port

        inc_address = Signal()
        address = Signal.like(port.adr)
        last_address = Signal()
        self.comb += \
            If(inc_address,
                port.adr.eq(address + 1)
            ).Else(
                port.adr.eq(0)
            )
        self.sync += address.eq(port.adr)
        self.comb += last_address.eq(address == len(packet)-1)

        fsm = FSM()
        self.submodules += fsm

        fsm.act("IDLE",
            If(repeat,
                NextState("OUTPUT")
            )
        )
        fsm.act("OUTPUT",
            self.stb.eq(1),
            inc_address.eq(1),
            If(last_address,
                NextState("IDLE")
            )
        )
        self.comb += self.data.eq(port.dat_r)


test_packet = [
    0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0xd5,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x08, 0x60,
    0x6e, 0x44, 0x42, 0x95, 0x08, 0x06, 0x00, 0x01,
    0x08, 0x00, 0x06, 0x04, 0x00, 0x01, 0x08, 0x60,
    0x6e, 0x44, 0x42, 0x95, 0xc0, 0xa8, 0x01, 0x64,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xc0, 0xa8,
    0x01, 0xe7, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x69, 0xd0, 0x85, 0x9f
]


class Transmitter(Module):
    def __init__(self, platform):
        self.clock_domains.cd_sys = ClockDomain()

        platform.toolchain.bitstream_commands.extend([
            "set_property BITSTREAM.GENERAL.COMPRESS True [current_design]",
            "set_property CFGBVS VCCO [current_design]",
            "set_property CONFIG_VOLTAGE 3.3 [current_design]",
            ])

        clk50_buffered = Signal()
        pll_locked = Signal()
        pll_fb = Signal()
        pll_eth_tx = Signal()
        pll_eth_tx_ext = Signal()
        self.specials += [
            Instance("BUFG", i_I=platform.request("clk50"), o_O=clk50_buffered),
            Instance("PLLE2_BASE", name="crg_main_mmcm",
                p_STARTUP_WAIT="FALSE", o_LOCKED=pll_locked,

                # VCO @ 1GHz
                p_REF_JITTER1=0.01, p_CLKIN1_PERIOD=20.0,
                p_CLKFBOUT_MULT=20, p_DIVCLK_DIVIDE=1,
                i_CLKIN1=clk50_buffered, i_CLKFBIN=pll_fb, o_CLKFBOUT=pll_fb,

                # 125MHz outputs
                p_CLKOUT0_DIVIDE=8, p_CLKOUT0_PHASE=0.0, o_CLKOUT0=pll_eth_tx,
                p_CLKOUT1_DIVIDE=8, p_CLKOUT1_PHASE=135.0, o_CLKOUT1=pll_eth_tx_ext,
            ),
            Instance("BUFG", i_I=pll_eth_tx, o_O=self.cd_sys.clk),
            AsyncResetSynchronizer(self.cd_sys, ~pll_locked)
        ]

        eth_clocks = platform.request("eth_clocks")
        pll_eth_tx_ext_buffered = Signal()
        self.specials += [
            Instance("BUFG", i_I=pll_eth_tx_ext, o_O=pll_eth_tx_ext_buffered),
            DDROutput(0, 1, eth_clocks.tx, pll_eth_tx_ext_buffered)
        ]

        traffic_generator = TrafficGenerator(test_packet, 26)
        self.submodules += traffic_generator

        phy = ClockDomainsRenamer({"eth_tx": "sys"})(
            LiteEthPHYRGMIITX(platform.request("eth_rgmii")))
        self.submodules += phy

        self.comb += [
            phy.sink.stb.eq(traffic_generator.stb),
            phy.sink.data.eq(traffic_generator.data)
        ]


def main():
    action = "synth"
    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2:
        action = sys.argv[1]
    else:
        raise SystemExit("Incorrect number of arguments")
    if action not in {"synth", "sim"}:
        raise SystemExit("Incorrect action")

    if action == "synth":
        platform = sayma_amc.Platform()
        top = Transmitter(platform)
        platform.build(top, build_dir="sayma_transmitter")
    elif action == "sim":
        dut = TrafficGenerator([1, 2, 3, 4, 5, 6], 4)
        run_simulation(dut, (None for _ in range(64)),
                       vcd_name="traffic_generator.vcd")
    else:
        raise ValueError

if __name__ == "__main__":
    main()
