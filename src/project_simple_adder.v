/*
 * Copyright (c) 2024 Weihua Xiao
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_koggestone_adder (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  wire [3:0] a, b;
  wire [3:0] sum;
  wire carry_out;
  wire [4:0] aplusb;
  
  assign a = ui_in[3:0];
  assign b = ui_in[7:4];
   
  assign aplusb = a + b;

  // Sum computation
  assign sum = aplusb[3:0];
  assign carry_out = aplusb[4];

  assign uo_out[3:0] = sum;
  assign uo_out[4] = carry_out; 
  assign uo_out[7:5] = 3'b000;
  assign uio_out = 8'b00000000;
  assign uio_oe = 8'b00000000;
endmodule