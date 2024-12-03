// -----------------------------------------------------------------------------
// Auto-Generated by:        __   _ __      _  __
//                          / /  (_) /____ | |/_/
//                         / /__/ / __/ -_)>  <
//                        /____/_/\__/\__/_/|_|
//                     Build your hardware, easily!
//                   https://github.com/enjoy-digital/litex
//
// Filename   : io_configurator_v1_0.v
// Device     : gemini
// LiteX sha1 : 4aa340d
// Date       : 2024-05-08 18:04:28
//------------------------------------------------------------------------------
// This file is Copyright (c) 2022 RapidSilicon
//--------------------------------------------------------------------------------

`timescale 1ns / 1ps

//------------------------------------------------------------------------------
// Module
//------------------------------------------------------------------------------

module io_configurator #(
	parameter IP_TYPE 		= "IO",
	parameter IP_VERSION 	= 32'h1, 
	parameter IP_ID 		= 32'h485611c
)
(
    input  wire    [3:0] FABRIC_D,
    input  wire          FABRIC_RST,
    input  wire          FABRIC_LOAD_WORD,
    input  wire          FABRIC_CLK_IN,
    input  wire          FABRIC_OE_IN,
    input  wire          FABRIC_DLY_LOAD,
    output wire          IOPAD_Q
);


//------------------------------------------------------------------------------
// Signals
//------------------------------------------------------------------------------

wire          q;
wire          q_1;
wire          oe_out;
wire          pll_clk;
wire          pll_lock;
wire          lo_clk;
wire    [5:0] open;
wire          open1;

//------------------------------------------------------------------------------
// Combinatorial Logic
//------------------------------------------------------------------------------



//------------------------------------------------------------------------------
// Synchronous Logic
//------------------------------------------------------------------------------


//------------------------------------------------------------------------------
// Specialized Logic
//------------------------------------------------------------------------------

BOOT_CLOCK BOOT_CLOCK(
	.O(lo_clk)
);

PLL #(
	.PLL_DIV(1'd1),
	.PLL_MULT(7'd80),
) PLL (
	.CLK_IN(lo_clk),
	.PLL_EN(1'd1),
	.CLK_OUT(pll_clk),
	.LOCK(pll_lock)
);

O_SERDES #(
	.DATA_RATE("SDR"),
	.WIDTH(3'd4)
) O_SERDES (
	.CHANNEL_BOND_SYNC_IN(1'd0),
	.CLK_IN(FABRIC_CLK_IN),
	.D(FABRIC_D),
	.LOAD_WORD(FABRIC_LOAD_WORD),
	.OE_IN(FABRIC_OE_IN),
	.PLL_CLK(pll_clk),
	.PLL_LOCK(pll_lock),
	.RST(FABRIC_RST),
	.CHANNEL_BOND_SYNC_OUT(open1),
	.OE_OUT(oe_out),
	.Q(q_1)
);

O_DELAY #(
	.DELAY(1'd0)
) O_DELAY (
	.CLK_IN(pll_clk),
	.DLY_ADJ(1'd0),
	.DLY_INCDEC(1'd0),
	.DLY_LOAD(FABRIC_DLY_LOAD),
	.I(q_1),
	.DLY_TAP_VALUE(open),
	.O(q)
);

O_BUFT O_BUFT(
	.I(q),
	.T(oe_out),
	.O(IOPAD_Q)
);

endmodule

// -----------------------------------------------------------------------------
//  Auto-Generated by LiteX on 2024-05-08 18:04:28.
//------------------------------------------------------------------------------
