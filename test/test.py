# By RickGao
from binascii import Error

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer


# Operation codes for R-Type instructions
R_TYPE_FUNCT3 = {
    "AND": 0b000,
    "OR":  0b001,
    "ADD": 0b010,
    "SUB": 0b011,
    "XOR": 0b001,  # With funct2 for XOR as 0b01
    "SLT": 0b111
}

# Operation codes for I-Type instructions
I_TYPE_FUNCT3 = {
    "SLL":  0b100,
    "SRL":  0b101,
    "SRA":  0b110,
    "ADDI": 0b010,
    "SUBI": 0b011
}

# Helper function to parse register names
REGISTER_MAP = {
    "x0": 0b000,
    "x1": 0b001,
    "x2": 0b010,
    "x3": 0b011,
    "x4": 0b100,
    "x5": 0b101,
    "x6": 0b110,
    "x7": 0b111
}

# Operation codes for B-Type instructions
B_TYPE_FUNCT3 = {
    "BEQ":  0b011,
    "BNE":  0b011,
    "BLT":  0b111,
}


class RegisterFileTracker:
    def __init__(self):
        # Initialize 8 registers with 8-bit signed integers, all set to 0
        self.registers = [0] * 8

    def update_register(self, register_name, value):
        """
        Update the value of a register.
        If the value exceeds the 8-bit signed integer range, it will be truncated.
        """
        register_index = REGISTER_MAP[register_name]
        # Ensure value is within 8-bit signed integer range
        if value > 127 or value < - 128:
            print(f"Value = {value}, out of range")
        self.registers[register_index] = value

    def get_register(self, register_name):
        """
        Retrieve the current value of a specific register.
        """
        register_index = REGISTER_MAP[register_name]
        return self.registers[register_index]

    def print_registers(self):
        """
        Print the current state of all registers.
        """
        print("Current Register Values:")
        for i in range(len(self.registers)):
            print(f"x{i}: {self.registers[i]}")
        print()


register_tracker = RegisterFileTracker()



# R-Type instruction function
async def r_type(dut, operation, rd, rs1, rs2, expected_output=0):
    funct3 = R_TYPE_FUNCT3[operation]
    funct2 = 0b01 if operation == "XOR" else 0b00  # Set funct2 for XOR
    rd_address = REGISTER_MAP[rd]
    rs1_address = REGISTER_MAP[rs1]
    rs2_address = REGISTER_MAP[rs2]
    opcode = 0b00

    # Log details
    dut._log.info(f"Executing R-Type Instruction: {operation} {rd}, {rs1}, {rs2}")
    dut._log.info(f"funct3: {funct3}, funct2: {funct2}, rs2: {rs2_address}, rs1: {rs1_address}, rd: {rd_address}, Opcode: {opcode}")

    # Set inputs and wait
    instruction = (funct3 << 13) | (funct2 << 11) | (rs2_address << 8) | (rs1_address << 5) | (rd_address << 2) | opcode
    dut.ui_in.value = instruction & 0xFF
    dut.uio_in.value = (instruction >> 8) & 0xFF
    await Timer(1, units="us")

    # Output result
    dut._log.info(f"Expected Output: {expected_output}, Actual Output: {dut.uo_out.value}\n")
    assert dut.uo_out.value == expected_output, f"Expected {expected_output}, got {dut.uo_out.value}"

    await ClockCycles(dut.clk, 1)

# I-Type instruction function
async def i_type(dut, operation, rd, rs1, imm, expected_output=0):
    funct3 = I_TYPE_FUNCT3[operation]
    rd_address = REGISTER_MAP[rd]
    rs1_address = REGISTER_MAP[rs1]
    opcode = 0b01

    # Log details
    dut._log.info(f"Executing I-Type Instruction: {operation} {rd}, {rs1}, {imm}")
    dut._log.info(f"funct3: {funct3}, Immediate: {imm}, rs1: {rs1_address}, rd: {rd_address}, Opcode: {opcode}")

    # Set inputs and wait
    instruction = (funct3 << 13) | (imm << 8) | (rs1_address << 5) | (rd_address << 2) | opcode
    dut.ui_in.value = instruction & 0xFF
    dut.uio_in.value = (instruction >> 8) & 0xFF
    await Timer(1, units="us")

    # Output result
    dut._log.info(f"Expected Output: {expected_output}, Actual Output: {dut.uo_out.value}\n")
    assert dut.uo_out.value == expected_output, f"Expected {expected_output}, got {dut.uo_out.value}"

    await ClockCycles(dut.clk, 1)

# L-Type instruction function
async def l_type(dut, rd, imm, expected_output=0):
    rd_address = REGISTER_MAP[rd]
    opcode = 0b10

    # Log details
    dut._log.info(f"Executing L-Type Instruction: LOAD {rd}, {imm}")
    dut._log.info(f"Immediate: {imm}, rd: {rd_address}, Opcode: {opcode}")

    # Set inputs and wait
    instruction = (imm << 8) | (rd_address << 2) | opcode
    dut.ui_in.value = instruction & 0xFF
    dut.uio_in.value = imm
    await Timer(1, units="us")

    # Output result
    dut._log.info(f"Expected Output: {expected_output}, Actual Output: {dut.uo_out.value}\n")
    assert dut.uo_out.value == expected_output, f"Expected {expected_output}, got {dut.uo_out.value}"

    await ClockCycles(dut.clk, 1)

# S-Type instruction function
async def s_type(dut, rs1, expected_output):
    rs1_address = REGISTER_MAP[rs1]
    opcode = 0b11

    # Log details
    dut._log.info(f"Executing S-Type Instruction: STORE {rs1}")
    dut._log.info(f"rs1: {rs1_address}, Opcode: {opcode}")

    # Set inputs and wait
    dut.ui_in.value = (rs1_address << 5) | opcode
    dut.uio_in.value = 0b00000000
    await Timer(1, units="us")

    # Output result
    dut._log.info(f"Expected Output: {expected_output}, Actual Output: {dut.uo_out.value}\n")
    assert dut.uo_out.value == expected_output, f"Expected {expected_output}, got {dut.uo_out.value}"

    await ClockCycles(dut.clk, 1)

# B-Type instruction function
async def b_type(dut, operation, rs1, rs2, expected_output):
    funct3 = B_TYPE_FUNCT3[operation]  # Using same funct3 mapping as R-type for simplicity
    funct2 = 0b10 if operation == "BNE" else 0b00  # Set funct2 for BNE
    rs1_address = REGISTER_MAP[rs1]
    rs2_address = REGISTER_MAP[rs2]
    opcode = 0b11

    # Log details
    dut._log.info(f"Executing B-Type Instruction: {operation} {rs1}, {rs2}")
    dut._log.info(f"Opcode: {opcode}, funct3: {funct3}, funct2: {funct2}, rs1: {rs1}, rs2: {rs2}")

    # Set inputs and wait
    instruction = (funct3 << 13) | (funct2 << 11) | (rs2_address << 8) | (rs1_address << 5) | opcode
    dut.ui_in.value = instruction & 0xFF
    dut.uio_in.value = (instruction >> 8) & 0xFF
    await Timer(1, units="us")

    # Output result
    dut._log.info(f"Expected Output: {expected_output}, Actual Output: {dut.uo_out.value}\n")
    assert dut.uo_out.value == expected_output, f"Expected {expected_output}, got {dut.uo_out.value}"

    await ClockCycles(dut.clk, 1)

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 10)

    dut._log.info("Testing various instructions")
    register_tracker.print_registers()

    # Test Load and Store
    await s_type(dut, "x0", 0)  # Example for S-Type Store
    await l_type(dut, "x0", 10)
    await s_type(dut, "x0", 0)
    await l_type(dut, "x2", 6)
    register_tracker.update_register("x2", 4)
    await l_type(dut, "x3", 3)
    register_tracker.update_register("x3", 3)
    await s_type(dut, "x3", register_tracker.get_register("x3"))
    await s_type(dut, "x2", register_tracker.get_register("x2"))

    # Test R type
    await r_type(dut, "AND","x4", "x2","x3")
    register_tracker.update_register("x4",register_tracker.get_register("x2") & register_tracker.get_register("x3"))
    await s_type(dut, "x4", register_tracker.get_register("x4"))
    await r_type(dut, "OR","x5","x2","x3")
    register_tracker.update_register("x5",register_tracker.get_register("x2") & register_tracker.get_register("x3"))
    await s_type(dut, "x5", register_tracker.get_register("x5"))
    

    # await r_type(dut, "ADD", "x3", "x1", "x2", expected_output=0b00000000)  # Example for R-Type ADD
    # await i_type(dut, "ADDI", "x3", "x1", imm=0b00001, expected_output=0b00000101)  # Example for I-Type ADDI
    # await l_type(dut, "x3", imm=0b11111111, expected_output=0b11111111)  # Example for L-Type Load
    # await s_type(dut, "x1", expected_output=0)  # Example for S-Type Store
    # await b_type(dut, "BEQ", "x1", "x2", expected_output=1)  # Example for B-Type BEQ
