/*
 * Copyright (c) 2024 RickGao
 */

`default_nettype none


// Define Width with Macro
`ifndef WIDTH
`define WIDTH 8
`endif



module alu (
    input  wire [3:0]        control,   // Control Signal
    input  wire [`WIDTH-1:0] a,         // Operand A
    input  wire [`WIDTH-1:0] b,         // Operand B
    output wire [`WIDTH-1:0] out,       // Output
    output wire              carry,     // Carry Out
    output wire              zero       // Zero Flag
);


    // ALU Control Signal Type
    localparam [3:0] 
        AND  = 4'b0000,
        OR   = 4'b0001,
        ADD  = 4'b0010,
        SUB  = 4'b0011,
        XOR  = 4'b1001,
        SLL  = 4'b0100,  // Shift Left Logical
        SRL  = 4'b0101,  // Shift Right Logical
        SRA  = 4'b0110,  // Shift Right Arithmatic
        SLT  = 4'b0111;  // Set Less Than Signed

    // Calculate sum and difference
    wire [`WIDTH:0] sum;
    wire [`WIDTH:0] dif;
    assign sum = {1'b0, a} + {1'b0, b};
    assign dif = {1'b0, a} - {1'b0, b};

    // Calculate bit of shift
    wire [$clog2(`WIDTH)-1:0] shift;
    assign shift = b[$clog2(`WIDTH)-1:0];
    // Shift right arithmatic
    wire [`WIDTH-1:0] right_shifted;
    assign right_shifted = a >> shift;
    // Calculate high bits
    wire [`WIDTH-1:0] sign_extend;
    assign sign_extend = a[`WIDTH-1] ? (~( {`WIDTH{1'b1}} >> shift )) : {`WIDTH{1'b0}};
    
    // Assign outputs based on the control signal
    assign out =    (control == AND) ? (a & b) :
                    (control == OR)  ? (a | b) :
                    (control == ADD) ? sum[`WIDTH-1:0] :
                    (control == SUB) ? dif[`WIDTH-1:0] :
                    (control == XOR) ? (a ^ b) :
                    (control == SLL) ? (a << shift) :
                    (control == SRL) ? (a >> shift) :
                    (control == SRA) ? (right_shifted | sign_extend) :
                    // (control == SRA) ? ($signed(a) >>> b[$clog2(`WIDTH)-1:0]): // Not working
                    (control == SLT) ? (($signed(a) < $signed(b)) ? {{(`WIDTH-1){1'b0}}, 1'b1} : {`WIDTH{1'b0}}) :
                    {`WIDTH{1'b0}};  // Default output is 0


    // Assign carry out for ADD and SUB operations
    assign carry =  (control == ADD) ? sum[`WIDTH] :
                    (control == SUB) ? dif[`WIDTH] :
                    1'b0;  // No carry for other operations

    // Zero Flag
    assign zero = (out == {`WIDTH{1'b0}});


    // assign uo_out[5:0] = out[5:0];
    // assign uo_out[6]   = carry;
    // assign uo_out[7]   = zero;

endmodule
