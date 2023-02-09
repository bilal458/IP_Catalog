#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT.

import os
import sys
import argparse

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface


# IOs / Interface ----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk", 0, Pins(1)),
        ("rst", 0, Pins(1))
        ]

def get_jtag_ios():
    return [
        ("jtag_tms",    0,  Pins(1)),
        ("jtag_tdi",    0,  Pins(1)),
        ("jtag_tdo",    0,  Pins(1)),
        ("jtag_tck",    0,  Pins(1))    
        ]

def get_other_ios(n):
    if (n == "base_variant"):
        return [
            ("debugReset",          0,  Pins(1)),
            ("debug_resetOut",      0,  Pins(1)),
            ("timerInterrupt",      0,  Pins(1)),
            ("externalInterrupt",   0,  Pins(1)),    
            ("softwareInterrupt",   0,  Pins(1))
        ]  
    if (n == "cached_with_mmu"):
        return [
            ("debugReset",          0,  Pins(1)),
            ("debug_resetOut",      0,  Pins(1)),
            ("timerInterrupt",      0,  Pins(1)),
            ("externalInterrupt",   0,  Pins(1)),    
            ("softwareInterrupt",   0,  Pins(1)),
            ("externalInterruptS",  0,  Pins(1)),
            ("utime",               0,  Pins(64))
        ]      
    if (n == "cached_with_mmu_plic_clint"):
        return [
            ("debugReset",          0,  Pins(1)),
            ("debug_resetOut",      0,  Pins(1)),
            ("clint_awvalid",       0,  Pins(1)),
            ("clint_awready",       0,  Pins(1)),
            ("clint_awaddr",        0,  Pins(16)),
            ("clint_awprot",        0,  Pins(3)),
            ("clint_wvalid",        0,  Pins(1)),
            ("clint_wready",        0,  Pins(1)),
            ("clint_wdata",         0,  Pins(32)),
            ("clint_wstrb",         0,  Pins(4)),
            ("clint_bvalid",        0,  Pins(1)),
            ("clint_bready",        0,  Pins(1)),
            ("clint_bresp",         0,  Pins(2)),
            ("clint_arvalid",       0,  Pins(1)),
            ("clint_arready",       0,  Pins(1)),
            ("clint_araddr",        0,  Pins(16)),
            ("clint_arprot",        0,  Pins(3)),
            ("clint_rvalid",        0,  Pins(1)),
            ("clint_rready",        0,  Pins(1)),
            ("clint_rdata",         0,  Pins(32)),
            ("clint_rresp",         0,  Pins(2)),
            ("plic_awvalid",        0,  Pins(1)),
            ("plic_awready",        0,  Pins(1)),
            ("plic_awaddr",         0,  Pins(16)),
            ("plic_awprot",         0,  Pins(3)),
            ("plic_wvalid",         0,  Pins(1)),
            ("plic_wready",         0,  Pins(1)),
            ("plic_wdata",          0,  Pins(32)),
            ("plic_wstrb",          0,  Pins(4)),
            ("plic_bvalid",         0,  Pins(1)),
            ("plic_bready",         0,  Pins(1)),
            ("plic_bresp",          0,  Pins(2)),
            ("plic_arvalid",        0,  Pins(1)),
            ("plic_arready",        0,  Pins(1)),
            ("plic_araddr",         0,  Pins(16)),
            ("plic_arprot",         0,  Pins(3)),
            ("plic_rvalid",         0,  Pins(1)),
            ("plic_rready",         0,  Pins(1)),
            ("plic_rdata",          0,  Pins(32)),
            ("plic_rresp",          0,  Pins(2)),
            ("plicInterrupts",      0,  Pins(32))
        ]
            

# AXI-VEXRISCV Wrapper --------------------------------------------------------------------------------
class GeminiPSSWrapper(Module):
    def __init__(self, platform, base_variant, cached_with_mmu, cached_with_mmu_plic_clint):
        
        # Clocking
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))

        #IBUS
        ibus_axi = AXIInterface(data_width = 32, address_width = 32, id_width = 8)
        platform.add_extension(ibus_axi.get_ios("ibus_axi"))
        self.comb += ibus_axi.connect_to_pads(platform.request("ibus_axi"), mode="master")

        #IBUS
        dbus_axi = AXIInterface(data_width = 32, address_width = 32, id_width = 8)
        platform.add_extension(dbus_axi.get_ios("dbus_axi"))
        self.comb += dbus_axi.connect_to_pads(platform.request("dbus_axi"), mode="master")

        if (base_variant):
            cpu_type = "base_variant"
            # VEXRISCV without cache and MMU
            self.submodules.vexriscv = vexriscv = vexriscv_nocache_nommu(platform,
                ibus        = ibus_axi,
                dbus        = dbus_axi
                )
        elif (cached_with_mmu):
            cpu_type = "cached_with_mmu"
            # VEXRISCV with Cache and MMU
            self.submodules.vexriscv = vexriscv = vexriscv_linux_mmu(platform,
                ibus        = ibus_axi,
                dbus        = dbus_axi
                )
        elif (cached_with_mmu_plic_clint):
            cpu_type = "cached_with_mmu_plic_clint"
            # VEXRISCV with Cache, MMU, PLIC and Clint
            self.submodules.vexriscv = vexriscv = vexriscv_plic_clint(platform,
                ibus        = ibus_axi,
                dbus        = dbus_axi
                )
        platform.add_extension(get_jtag_ios())
        # Inputs
        self.comb += vexriscv.jtag_tms.eq(platform.request("jtag_tms"))
        self.comb += vexriscv.jtag_tdi.eq(platform.request("jtag_tdi"))
        self.comb += vexriscv.jtag_tck.eq(platform.request("jtag_tck"))

        # Outputs
        self.comb += platform.request("jtag_tdo").eq(vexriscv.jtag_tdo)

        platform.add_extension(get_other_ios(cpu_type))
        # Inputs
        self.comb += vexriscv.debugReset.eq(platform.request("debugReset"))
        if (base_variant or cached_with_mmu):
            self.comb += vexriscv.timerInterrupt.eq(platform.request("timerInterrupt"))
            self.comb += vexriscv.externalInterrupt.eq(platform.request("externalInterrupt"))
            self.comb += vexriscv.softwareInterrupt.eq(platform.request("softwareInterrupt"))
            if (cached_with_mmu):
                self.comb += vexriscv.externalInterruptS.eq(platform.request("externalInterruptS"))
                self.comb += vexriscv.utime.eq(platform.request("utime"))
        if (cached_with_mmu_plic_clint):
            self.comb += vexriscv.clint_awvalid.eq(platform.request("clint_awvalid"))
            self.comb += vexriscv.clint_awaddr.eq(platform.request("clint_awaddr"))
            self.comb += vexriscv.clint_awprot.eq(platform.request("clint_awprot"))
            self.comb += vexriscv.clint_wvalid.eq(platform.request("clint_wvalid"))
            self.comb += vexriscv.clint_wdata.eq(platform.request("clint_wdata"))
            self.comb += vexriscv.clint_wstrb.eq(platform.request("clint_wstrb"))
            self.comb += vexriscv.clint_bready.eq(platform.request("clint_bready"))
            self.comb += vexriscv.clint_arvalid.eq(platform.request("clint_arvalid"))
            self.comb += vexriscv.clint_araddr.eq(platform.request("clint_araddr"))
            self.comb += vexriscv.clint_arprot.eq(platform.request("clint_arprot"))
            self.comb += vexriscv.clint_rready.eq(platform.request("clint_rready"))
            self.comb += vexriscv.plic_awvalid.eq(platform.request("plic_awvalid"))
            self.comb += vexriscv.plic_awaddr.eq(platform.request("plic_awaddr"))
            self.comb += vexriscv.plic_awprot.eq(platform.request("plic_awprot"))
            self.comb += vexriscv.plic_wvalid.eq(platform.request("plic_wvalid"))
            self.comb += vexriscv.plic_wdata.eq(platform.request("plic_wdata"))
            self.comb += vexriscv.plic_wstrb.eq(platform.request("plic_wstrb"))
            self.comb += vexriscv.plic_bready.eq(platform.request("plic_bready"))
            self.comb += vexriscv.plic_arvalid.eq(platform.request("plic_arvalid"))
            self.comb += vexriscv.plic_araddr.eq(platform.request("plic_araddr"))
            self.comb += vexriscv.plic_arprot.eq(platform.request("plic_arprot"))
            self.comb += vexriscv.plic_rready.eq(platform.request("plic_rready"))
            self.comb += vexriscv.plicInterrupts.eq(platform.request("plicInterrupts"))
            # Outputs
            self.comb += platform.request("clint_awready").eq(vexriscv.clint_awready)
            self.comb += platform.request("clint_wready").eq(vexriscv.clint_wready)
            self.comb += platform.request("clint_bvalid").eq(vexriscv.clint_bvalid)
            self.comb += platform.request("clint_bresp").eq(vexriscv.clint_bresp)
            self.comb += platform.request("clint_arready").eq(vexriscv.clint_arready)
            self.comb += platform.request("clint_rvalid").eq(vexriscv.clint_rvalid)
            self.comb += platform.request("clint_rdata").eq(vexriscv.clint_rdata)
            self.comb += platform.request("clint_rresp").eq(vexriscv.clint_rresp)
            self.comb += platform.request("plic_awready").eq(vexriscv.plic_awready)
            self.comb += platform.request("plic_wready").eq(vexriscv.plic_wready)
            self.comb += platform.request("plic_bvalid").eq(vexriscv.plic_bvalid)
            self.comb += platform.request("plic_bresp").eq(vexriscv.plic_bresp)
            self.comb += platform.request("plic_arready").eq(vexriscv.plic_arready)
            self.comb += platform.request("plic_rvalid").eq(vexriscv.plic_rvalid)
            self.comb += platform.request("plic_rdata").eq(vexriscv.plic_rdata)
            self.comb += platform.request("plic_rresp").eq(vexriscv.plic_rresp)
        self.comb += platform.request("debug_resetOut").eq(vexriscv.debug_resetOut)

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Rapid Silicon Gemini PSS")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="gemini_pss", language="verilog")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="gemini_pss_wrapper",     help="Build Folder Name, Build RTL File Name and Module Name")
    build_group.add_argument("--lang",   default="verilog",  help="Gemini PSS wrapper RTL language")
    
    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                    help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",     help="Generate JSON Template")

    args = parser.parse_args()
    
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)

    # Providing a default value
    if (not args.base_variant and not args.cached_with_mmu and not args.cached_with_mmu_plic_clint):
        args.base_variant = True

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = GeminiPSSWrapper(platform, base_variant=args.base_variant, cached_with_mmu=args.cached_with_mmu, cached_with_mmu_plic_clint=args.cached_with_mmu_plic_clint)
    
    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder.prepare(
            build_dir  = args.build_dir,
            build_name = args.build_name,
            version    = "v1_0"
        )
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()
        rs_builder.generate_wrapper(
            platform   = platform,
            module     = module,
        )
        
if __name__ == "__main__":
    main()