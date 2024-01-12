
`timescale 1ns / 1ps

//------------------------------------------------------------------------------
// Module
//------------------------------------------------------------------------------

module FIR_generator (
    input  wire   [17:0] data_in,
    output reg   [19:0] data_out,
    input  wire          clk,
    input  wire          rst
);

// Define the coefficients
  localparam COEFF_0 = 1048551;
  localparam COEFF_1 = 51;
  localparam COEFF_2 = 102;
  localparam COEFF_3 = 51;
  reg [17:0] delay_in1;
  reg [17:0] delay_in2;
  reg [17:0] delay_in3;
  reg [17:0] delay_in4;
  reg [17:0] delay_in5;
  reg [17:0] delay_in6;
  reg [17:0] delay_in7;
  wire [17:0] delay_b_0;
  wire [19:0] data_out1;

  always @(posedge clk) begin
    delay_in1 <= data_in;
    delay_in2 <= delay_in1;
    delay_in3 <= delay_in2;
    delay_in4 <= delay_in3;
    delay_in5 <= delay_in4;
    delay_in6 <= delay_in5;
    delay_in7 <= delay_in6;
    delay_in8 <= delay_in7;
    delay_in9 <= delay_in8;
    delay_in10 <= delay_in9;
  end
  reg [19:0] data_reg;
  reg [3:0] count = 4'd0;
  reg [19:0] data_out_reg;
  always @(posedge clk) begin
    if (count == 0 || count == 1 || count == 3 || count == 6) begin
      data_out_reg <= data_out1;
      data_reg <= data_out1;
    end else begin
      data_out_reg <= data_reg;
    end
    if (count == 9) begin
      count <= 6;
    end else
      count <= count + 1;
  end
  reg [17:0] dsp_input;
  reg [19:0] select_coeff;
  reg [2:0] feed;
  always @(*) begin
    if (count == 0) begin
      dsp_input <= data_in;
      select_coeff <= COEFF_0;
      feed <= 0;
      data_out <= data_out1;
    end else if (count < 3) begin
      dsp_input <= delay_in1;
      if (count == 1) begin
        select_coeff <= COEFF_1;
        feed = 1;
        data_out <= data_out1;
      end else begin
        select_coeff <= COEFF_0;
        feed = 0;
        data_out <= data_out_reg;
      end
    end else if (count < 6) begin
      dsp_input <= delay_in3;
      if (count == 3) begin
        select_coeff <= COEFF_2;
        feed = 1;
        data_out <= data_out1;
      end else if (count == 4) begin
        select_coeff <= COEFF_1;
        feed = 0;
        data_out <= data_out_reg;
      end else begin
        select_coeff <= COEFF_0;
        feed = 0;
        data_out <= data_out_reg;
      end
    end else if (count < 10) begin
      dsp_input <= delay_in6;
      if (count == 6) begin
        select_coeff <= COEFF_3;
        feed = 1;
        data_out <= data_out1;
      end else if (count == 7) begin
        select_coeff <= COEFF_2;
        feed = 0;
        data_out <= data_out_reg;
      end else if (count == 8) begin
        select_coeff <= COEFF_1;
        feed = 0;
        data_out <= data_out_reg;
      end else begin
        select_coeff <= COEFF_0;
        feed = 0;
        data_out <= data_out_reg;
      end
    end
  end

DSP38 #(
	.DSP_MODE("MULTIPLY_ACCUMULATE"),
	.INPUT_REG_EN("FALSE"),
	.OUTPUT_REG_EN("FALSE")
) DSP38 (
	.A(select_coeff),
	.B(dsp_input),
	.CLK(clk),
	.FEEDBACK(feed),
	.LOAD_ACC(1'd1),
	.RESET(rst),
	.ROUND(1'd0),
	.SATURATE(1'd0),
	.SHIFT_RIGHT(6'd0),
	.SUBTRACT(1'd0),
	.UNSIGNED_A(1'd0),
	.UNSIGNED_B(1'd1),
	.DLY_B(delay_b_0),
	.Z(data_out1)
);

endmodule