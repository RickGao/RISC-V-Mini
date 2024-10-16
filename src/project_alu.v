module tt_um_alu (
    input [3:0] op,            // Operation code to select the type of operation
    input [31:0] a,            // Operand 'a'
    input [31:0] b,            // Operand 'b'
    input [4:0] shamt,         // Shift amount (for shift operations)
    output [31:0] d,           // Result output
    output zero,               // Zero flag
    output less_than,          // Comparison flag for SLT and SLTU instructions
    output carry_out           // Carry output, used only for addition and subtraction
);

    // Define the logic for each operation
    wire [31:0] sum = a + b;                   // Result for addition
    wire [31:0] sub = a - b;                   // Result for subtraction
    wire [31:0] and_result = a & b;            // Result for AND operation
    wire [31:0] or_result = a | b;             // Result for OR operation
    wire [31:0] xor_result = a ^ b;            // Result for XOR operation
    wire [31:0] sll_result = a << shamt;       // Logical left shift
    wire [31:0] srl_result = a >> shamt;       // Logical right shift
    wire [31:0] sra_result = a >>> shamt;      // Arithmetic right shift

    // Unsigned comparison: checks if 'a' is less than 'b' (for SLTU)
    wire sltu_result = (a < b);
    // Signed comparison: checks if 'a' is less than 'b' (for SLT)
    wire slt_result = ($signed(a) < $signed(b));

    // Use a multiplexer to select the result based on the operation code
    assign d = (op == 4'b0000) ? sum :                 // ADD
               (op == 4'b1000) ? sub :                 // SUB
               (op == 4'b0010) ? {31'b0, slt_result} : // SLT (signed comparison)
               (op == 4'b0011) ? {31'b0, sltu_result} :// SLTU (unsigned comparison)
               (op == 4'b0111) ? and_result :          // AND
               (op == 4'b0110) ? or_result :           // OR
               (op == 4'b0100) ? xor_result :          // XOR
               (op == 4'b0001) ? sll_result :          // SLL (logical left shift)
               (op == 4'b0101) ? srl_result :          // SRL (logical right shift)
               (op == 4'b1101) ? sra_result :          // SRA (arithmetic right shift)
               32'b0;

    // Define output flag signals
    assign zero = (d == 32'b0);           // Zero flag, set if the result 'd' is zero
    assign less_than = slt_result;        // Less-than flag, used for signed comparison
    assign carry_out = (op == 4'b0000) ? sum[31] :     // Carry out for addition
                       (op == 4'b1000) ? sub[31] :     // Carry out for subtraction
                       1'b0;                           // No carry for other operations

endmodule
