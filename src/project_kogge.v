/*
 * Copyright (c) 2024 Weihua Xiao
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_koggestone_adder4 (
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
  
  assign a = ui_in[3:0];
  assign b = ui_in[7:4];
   

  wire [3:0] p; // Propagate
  wire [3:0] g; // Generate
  wire [3:0] c; // Carry

  // Precompute generate and propagate signals
  assign p = a ^ b; // Propagate
  assign g = a & b; // Generate

  // Stage 1: Compute generate signals for neighbor 1-bit pairs
  wire g1_1, g1_2, g1_3;
  wire p1_1, p1_2, p1_3; 
  assign g1_1 = g[1] | (p[1] & g[0]);   // Combine 1st and 0th bits
  assign g1_2 = g[2] | (p[2] & g[1]);   // Combine 2nd and 1st bits
  assign p1_2 = p[2] & p[1];	
  assign g1_3 = g[3] | (p[3] & g[2]);   // Combine 3rd and 2nd bits
  assign p1_3 = p[3] & p[2];

  // Stage 2: Compute generate signals for 2-bit groups
  wire g2_2, g2_3;
  assign g2_2 = g1_2 | (p1_2 & g[0]);   // Combine 2-bit group (2nd and 0th bits)
  assign g2_3 = g1_3 | (p1_3 & g1_1);   // Combine 2-bit group (3rd and 1st bits)

  // Compute final carry signals
  assign c[0] = 0;                      // No carry into the first bit
  assign c[1] = g[0];                   // Carry for 1st bit
  assign c[2] = g1_1;                   // Carry for 2nd bit
  assign c[3] = g2_2;                   // Carry for 3rd bit
  assign carry_out = g2_3;              // Carry-out

  // Sum computation
  assign sum = p ^ c;                               // XOR of propagate and carry

  assign uo_out[3:0] = sum;
  assign uo_out[4] = carry_out; 
  assign uo_out[7:5] = 3'b000;
  assign uio_out = 8'b00000000;
  assign uio_oe = 8'b00000000;
endmodule