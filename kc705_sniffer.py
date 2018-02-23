#!/usr/bin/env python3

from migen import *
from migen.build.platforms import kc705

from misoc.cores.liteeth_mini.phy.gmii import LiteEthPHYGMII

from microscope import *


class Sniffer(Module):
    def __init__(self, platform):
        self.clock_domains.cd_sys = ClockDomain(reset_less=True)
        clk156 = platform.request("clk156")
        self.specials += Instance("IBUFGDS", i_I=clk156.p, i_IB=clk156.n, o_O=self.cd_sys.clk)
        clk_freq = 156e6

        self.submodules += Microscope(platform.request("serial"), clk_freq)

        eth_clocks = platform.request("eth_clocks")
        eth_phy = LiteEthPHYGMII(eth_clocks, platform.request("eth"))
        self.submodules += eth_phy

        stb_r = Signal()
        sof = Signal()
        self.sync.eth_rx += stb_r.eq(eth_phy.source.stb)
        self.comb += sof.eq(eth_phy.source.stb & ~stb_r)

        stb_data = Signal(9)
        self.comb += stb_data.eq(Cat(eth_phy.source.data, eth_phy.source.stb))
        self.submodules += add_probe_buffer("eth", "data", stb_data,
                                            trigger=sof, depth=128,
                                            clock_domain="eth_rx")


def main():
    platform = kc705.Platform()
    top = Sniffer(platform)
    platform.build(top, build_dir="kc705_sniffer")

if __name__ == "__main__":
    main()
