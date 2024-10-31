/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none


// Define Width with Macro
`ifndef WIDTH
`define WIDTH 8
`endif


module tt_um_riscv_mini (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    // Bidirectional Pins All Input
    assign uio_oe  = 8'b00000000;

    // All output pins must be assigned. If not used, assign to 0.
    assign uio_out = 0;


    // Input and Output of CPU
    wire [15:0] instruction,       // 16-bit instruction input
    wire [7:0] result              // Result of the executed instruction


    // Connect pin to instruction
    assign instruction [7:0]  = ui_in [7:0];    // Lower 8 bits are Input pins
    assign instruction [15:8] = uio_in [7:0];   // Upper 8 bits are IO pins


    // Signal declarations
    wire [1:0] opcode;             // Opcode field of the instruction
    wire [2:0] rd, rs1, rs2;       // Destination and source registers
    wire [6:0] imm;                // Immediate value (for I-type instructions)
    wire [3:0] funct3;             // Function code for operation types
    wire [`WIDTH-1:0] reg_data1;   // Data from register 1
    wire [`WIDTH-1:0] reg_data2;   // Data from register 2
    wire [`WIDTH-1:0] alu_result;  // ALU output result
    wire alu_zero, alu_carry;      // ALU flag signals

    // Parse fields from the instruction
    assign opcode = instruction[1:0];
    assign rd     = instruction[10:8];
    assign rs1    = instruction[7:5];
    assign rs2    = instruction[4:2];
    assign imm    = instruction[10:4];
    assign funct3 = instruction[13:11];

    // Write enable signal based on opcode
    wire we;                       
    assign we = (opcode == 2'b00) || (opcode == 2'b01);  // Enabled for R-type and I-type instructions

    // Instruction type detection
    wire is_r_type = (opcode == 2'b00);
    wire is_i_type = (opcode == 2'b01);
    wire is_l_type = (opcode == 2'b10);
    wire is_s_type = (opcode == 2'b11 && funct3 == 3'b001);
    wire is_b_type = (opcode == 2'b11 && (funct3 == 3'b010 || funct3 == 3'b011));

    // ALU control signal based on funct3
    wire [3:0] alu_control;
    assign alu_control = (funct3 == 3'b000) ? 4'b0000 : // AND
                         (funct3 == 3'b001) ? 4'b0001 : // OR
                         (funct3 == 3'b010) ? 4'b0010 : // ADD
                         (funct3 == 3'b011) ? 4'b0110 : // SUB
                         (funct3 == 3'b100) ? 4'b0100 : // XOR
                         (funct3 == 3'b101) ? 4'b0011 : // SLL
                         (funct3 == 3'b110) ? 4'b0101 : // SRL
                         (funct3 == 3'b111) ? 4'b0111 : // SRA
                         4'b0000;                       // Default to AND

    // Instantiate the register file
    register reg_file (
        .clk(clk),
        .rst_n(rst_n),
        .read_reg1(rs1),
        .read_reg2(rs2),
        .write_reg(rd),
        .we(we),
        .write_data(is_i_type ? imm[`WIDTH-1:0] : alu_result),
        .read_data1(reg_data1),
        .read_data2(reg_data2)
    );

    // Instantiate the ALU
    alu alu_inst (
        .control(alu_control),
        .a(reg_data1),
        .b(is_i_type ? imm[`WIDTH-1:0] : reg_data2),
        .out(alu_result),
        .carry(alu_carry),
        .zero(alu_zero)
    );

    // Generate output result based on instruction type
    assign result = is_l_type ? reg_data1 :  // Load operation outputs register data
                    is_s_type ? reg_data2 :  // Store operation outputs register data
                    is_b_type ? {7'b0, (alu_zero || alu_carry)} : // Branch (BEQ/BLT) based on flags
                    alu_result; // Default output is ALU result

    // Connect output
    assign uo_out[7:0] = result[7:0];
  

endmodule
