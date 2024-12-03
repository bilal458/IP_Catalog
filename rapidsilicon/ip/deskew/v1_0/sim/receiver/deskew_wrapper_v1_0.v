// -----------------------------------------------------------------------------
// Auto-Generated by:        __   _ __      _  __
//                          / /  (_) /____ | |/_/
//                         / /__/ / __/ -_)>  <
//                        /____/_/\__/\__/_/|_|
//                     Build your hardware, easily!
//                   https://github.com/enjoy-digital/litex
//
// Filename   : deskew_wrapper_v1_0.v
// Device     : virgo
// LiteX sha1 : --------
// Date       : 2024-11-29 09:46:10
//------------------------------------------------------------------------------
// This file is Copyright (c) 2022 RapidSilicon
//--------------------------------------------------------------------------------

`timescale 1ns / 1ps

//------------------------------------------------------------------------------
// Module
//------------------------------------------------------------------------------

module deskew_wrapper #(
	parameter IP_TYPE 		= "DSKW",
	parameter IP_VERSION 	= 32'h1, 
	parameter IP_ID 		= 32'h5db9b8a
)
(
    input  wire          CLK_IN,
    input  wire          RST,
    input  wire    [7:0] DATA_IN,
    input  wire    [5:0] DLY_TAP_VALUE,
    output wire          DLY_LOAD,
    output wire          DLY_ADJ,
    output wire          DLY_INCDEC,
    output wire          DLY_SEL,
    output wire          CALIB_DONE,
    output wire          CALIB_ERROR
);


//------------------------------------------------------------------------------
// Signals
//------------------------------------------------------------------------------


//------------------------------------------------------------------------------
// Combinatorial Logic
//------------------------------------------------------------------------------



//------------------------------------------------------------------------------
// Synchronous Logic
//------------------------------------------------------------------------------


//------------------------------------------------------------------------------
// Specialized Logic
//------------------------------------------------------------------------------

deskew_cntrl_wrap #(
	.FREQ(11'd1600),
	.NUM_DLY(1'd1),
	.SAMPLES_NO(4'd10),
	.WIDTH(4'd8)
) deskew_cntrl_wrap (
	.clk(CLK_IN),
	.datain(DATA_IN),
	.dly_tap_value_in(DLY_TAP_VALUE),
	.rst(RST),
	.calib_done(CALIB_DONE),
	.calib_error(CALIB_ERROR),
	.dly_adj(DLY_ADJ),
	.dly_incdec(DLY_INCDEC),
	.dly_ld(DLY_LOAD),
	.dly_sel(DLY_SEL)
);

endmodule

// -----------------------------------------------------------------------------
//  Auto-Generated by LiteX on 2024-11-29 09:46:10.
//------------------------------------------------------------------------------