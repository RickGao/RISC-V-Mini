/*
 * Copyright (c) 2024 RickGao
 */

`default_nettype none


// Define Width with Macro
`ifndef WIDTH
`define WIDTH 8
`endif



// module tt_um_register (
//     input  wire [7:0] ui_in,    // Dedicated inputs
//     output wire [7:0] uo_out,   // Dedicated outputs
//     input  wire [7:0] uio_in,   // IOs: Input path
//     output wire [7:0] uio_out,  // IOs: Output path
//     output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
//     input  wire       ena,      // always 1 when the design is powered, so you can ignore it
//     input  wire       clk,      // clock
//     input  wire       rst_n     // reset_n - low to reset
// );

//     // Bidirectional Pins All Input
//     assign uio_oe  = 8'b00000000;

//     // All output pins must be assigned. If not used, assign to 0.
//     assign uio_out = 0;


//     wire [2:0] read_reg1;               // 3-bit address for read register 1
//     wire [2:0] read_reg2;               // 3-bit address for read register 2
//     wire [2:0] write_reg;               // 3-bit address for write register
//     wire we;                            // Write enable
//     wire [`WIDTH-1:0] write_data;       // Data to write, width defined by macro
//     wire [`WIDTH-1:0] read_data1;        // Output data from register 1
//     wire [`WIDTH-1:0] read_data2;        // Output data from register 2

//     // Input[7] and Input[3] disconnected
//     assign read_reg1[2:0]  = ui_in[2:0];    // Input[2:0] is read register 1
//     assign read_reg2[2:0]  = ui_in[6:4];    // Input[6:4] is read register 2

//     assign write_data[3:0] = uio_in[3:0];   // Lower 4 bit of IO is write data
//     assign write_reg[2:0]  = uio_in[6:4];   // IO[6:4] is write register
//     assign we              = uio_in[7];     // IO[7] is write enable



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
