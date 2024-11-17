/*
 * Copyright (c) 2024 RickGao
 */

`default_nettype none


// Define Width with Macro
`ifndef WIDTH
`define WIDTH 8
`endif



module register(
    input wire clk,                         // Clock signal
    input wire rst_n,                       // Reset signal
    input wire [2:0] read_reg1,             // 3-bit address for read register 1
    input wire [2:0] read_reg2,             // 3-bit address for read register 2
    input wire [2:0] write_reg,             // 3-bit address for write register
    input wire we,                          // Write enable
    input wire [`WIDTH-1:0] write_data,     // Data to write, width defined by macro
    output wire [`WIDTH-1:0] read_data1,    // Output data from register 1
    output wire [`WIDTH-1:0] read_data2     // Output data from register 2
);


    // 8 registers with width defined by macro
    reg [`WIDTH-1:0] registers [7:0];


    // Asynchronous read to wire
    assign read_data1 = registers[read_reg1];
    assign read_data2 = registers[read_reg2];
    
    // // Asynchronous read to register
    // always @(*) begin
    //     read_data1 = registers[read_reg1];
    //     read_data2 = registers[read_reg2];
    // end


    // Synchronous write
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            // Reset all registers to 0 on reset
            registers[0] <= 0;
            registers[1] <= 0;
            registers[2] <= 0;
            registers[3] <= 0;
            registers[4] <= 0;
            registers[5] <= 0;
            registers[6] <= 0;
            registers[7] <= 0;
        end else if (we && write_reg != 3'b000) begin
            // Write to the register (skip register 0 to maintain x0 as always zero)
            registers[write_reg] <= write_data;
        end
    end

    
    // assign uo_out[3:0] = read_data1[3:0];   // Lower 4 bit of output is read data 1
    // assign uo_out[7:4] = read_data2[3:0];   // Upper 4 bit of output is read data 2

endmodule
