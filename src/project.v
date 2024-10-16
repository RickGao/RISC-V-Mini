/*
 * Copyright (c) 2024 RickGao
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

  // List all unused inputs to prevent warnings
  // wire _unused = &{ena, clk, rst_n, 1'b0};


  // All output pins must be assigned. If not used, assign to 0.
  assign uio_out = 8'b00000000;
  assign uio_oe = 8'b00000000;

  wire[3:0] a, b;
  assign a = ui_in[3:0];
  assign b = ui_in[7:4];
  
  wire[3:0] gen, pro; // Generate, Propagate
  assign gen = a & b;
  assign pro = a ^ b;


  // Layer 1   i - 1
  wire gen1_l1, gen2_l1, gen3_l1, pro2_l1, pro3_l1;
  assign gen1_l1 = gen[1] | (pro[1] & gen[0]);
  assign gen2_l1 = gen[2] | (pro[2] & gen[1]);
  assign gen3_l1 = gen[3] | (pro[3] & gen[2]);
  assign pro2_l1 = pro[2] & pro[1];
  assign pro3_l1 = pro[3] & pro[2];

  // Layer 2   i - 2
  wire gen2_l2, gen3_l2;
  assign gen2_l2 = gen2_l1 | (pro2_l1 & gen[0]);
  assign gen3_l2 = gen3_l1 | (pro3_l1 & gen1_l1);
  
  // Output
  wire[3:0] carry, sum;
  wire carry_out;
  assign carry[0] = 0;
  assign carry[1] = gen[0];
  assign carry[2] = gen1_l1;
  assign carry[3] = gen2_l2;
  assign carry_out = gen3_l2; 

  assign sum = pro ^ carry;
  
  assign uo_out[3:0] = sum;
  assign uo_out[4] = carry_out;

  assign uo_out[7:5] = 3'b000;
  assign uio_out = 8'b00000000;
  assign uio_oe = 8'b00000000;

endmodule
