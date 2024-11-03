# By RickGao

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer
from random import randint, choice


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

reg_namelist = ["x0", "x1", "x2", "x3", "x4", "x5", "x6", "x7"]

def to_int(value):

    # Convert an integer to an 8-bit signed integer in the range of -128 to 127.
    value = int(value) & 0xFF  # Ensure value is within 0 to 255

    if value > 127:
        return value - 256     # Convert to signed negative value
    else:
        return value           # Value is already within -128 to 127


def to_bin(value):

    if value < -128 or value > 127:
        raise ValueError("Value must be within the range of an 8-bit signed integer (-128 to 127)")

    # 8 bit binary
    if value >= 0:
        binary_value = value & 0xFF
    else:
        binary_value = (value + 256) & 0xFF

    return binary_value


def shift_right_logical(value, shamt):
    # Ensure the value is in 8-bit range (-128 to 127)
    if value < -128 or value > 127:
        raise ValueError("Value must be within the range of an 8-bit signed integer (-128 to 127)")

    # Convert to 8-bit unsigned equivalent
    unsigned_value = value & 0xFF  # Mask to 8 bits

    # Perform logical right shift
    shifted = unsigned_value >> shamt

    # Mask again to ensure it fits within 8 bits
    return to_int(shifted & 0xFF)


class RegisterFileTracker:
    def __init__(self):
        # Initialize 8 registers with 8-bit signed integers, all set to 0
        self.registers = [0] * 8

    def update(self, register_name, value):
        # Update the value of a register.
        # If the value exceeds the 8-bit signed integer range, it will be truncated.
        register_index = REGISTER_MAP[register_name]
        # Ensure value is within 8-bit signed integer range
        if value > 127 or value < - 128:
            print(f"Value = {value}, out of range")
        if register_name == "x0":
            return
        self.registers[register_index] = value

    def get(self, register_name):
        # Retrieve the current value of a specific register.
        register_index = REGISTER_MAP[register_name]
        return self.registers[register_index]

    def print_all(self):
        # Print the current state of all registers.
        print("Current Register Values:")
        for i in range(len(self.registers)):
            print(f"x{i}: {self.registers[i]}")
        print()

    def reset(self):
        print("Register Tracker Reset")
        self.registers = [0] * 8


register = RegisterFileTracker()



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
    imm = to_bin(imm)
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

    actual_output = to_int(dut.uo_out.value)  # Convert to signed 8-bit
    dut._log.info(f"Expected Output: {expected_output}, Actual Output: {actual_output}\n")
    assert actual_output == expected_output, f"Expected {expected_output}, got {actual_output}"

    # # Output result
    # dut._log.info(f"Expected Output: {expected_output}, Actual Output: {dut.uo_out.value}\n")
    # assert dut.uo_out.value == expected_output, f"Expected {expected_output}, got {dut.uo_out.value}"

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

    register.reset()
    register.print_all()

    print("Testing instructions\n")

    print("Test Load and Store\n")
    # Test Load and Store
    # Test x0
    await s_type(dut, "x0", 0)
    await l_type(dut, "x0", 10)
    await s_type(dut, "x0", 0)
    # Test x1 to x7
    for rd in reg_namelist[1:]:
        await l_type(dut, rd, 127)
        register.update(rd, 127)
        await s_type(dut, rd, register.get(rd))
        await l_type(dut, rd, -128)
        register.update(rd, -128)
        await s_type(dut, rd, register.get(rd))
        for i in range(3):
            imm = randint(-128, 127)
            await l_type(dut, rd, imm)
            register.update(rd, imm)
            await s_type(dut, rd, register.get(rd))

    print("Test R-Type\n")
    print("Test AND\n")
    register.print_all()

    rd = choice(reg_namelist[1:])
    rs1 = choice(reg_namelist)
    await r_type(dut, "AND", rd, rs1, "x0")
    register.update(rd, to_int(register.get(rs1) & 0))
    await s_type(dut, rd, register.get(rd))

    await l_type(dut, "x7", -1)
    register.update("x7", -1)
    rd = choice(reg_namelist[1:])
    rs1 = choice(reg_namelist)
    await r_type(dut, "AND", rd, rs1, "x7")
    register.update(rd, to_int(register.get(rs1) & register.get("x7")))
    await s_type(dut, rd, register.get(rd))

    for i in range(10):
        rd = choice(reg_namelist[1:])
        rs1 = choice(reg_namelist)
        rs2 = choice(reg_namelist)
        await r_type(dut, "AND", rd, rs1, rs2)
        register.update(rd, to_int(register.get(rs1) & register.get(rs2)))
        await s_type(dut, rd, register.get(rd))

    print("Test OR\n")
    register.print_all()

    for rd in reg_namelist[1:]:
        imm = randint(-128, 127)
        await l_type(dut, rd, imm)
        register.update(rd, imm)
    register.print_all()

    rd = choice(reg_namelist[1:])
    rs1 = choice(reg_namelist)
    await r_type(dut, "OR", rd, rs1, "x0")
    register.update(rd, to_int(register.get(rs1) | 0))
    await s_type(dut, rd, register.get(rd))

    await l_type(dut, "x7", -1)
    register.update("x7", -1)
    rd = choice(reg_namelist[1:])
    rs1 = choice(reg_namelist)
    await r_type(dut, "OR", rd, rs1, "x7")
    register.update(rd, to_int(register.get(rs1) | register.get("x7")))
    await s_type(dut, rd, register.get(rd))

    for i in range(10):
        rd = choice(reg_namelist[1:])
        rs1 = choice(reg_namelist)
        rs2 = choice(reg_namelist)
        await r_type(dut, "OR", rd, rs1, rs2)
        register.update(rd, to_int(register.get(rs1) | register.get(rs2)))
        await s_type(dut, rd, register.get(rd))


    print("Test ADD\n")
    register.print_all()

    for rd in reg_namelist[1:]:
        imm = randint(-128, 127)
        await l_type(dut, rd, imm)
        register.update(rd, imm)
    register.print_all()

    for i in range(20):
        rd = choice(reg_namelist[1:])
        rs1 = choice(reg_namelist)
        rs2 = choice(reg_namelist)
        await r_type(dut, "ADD", rd, rs1, rs2)
        register.update(rd, to_int(register.get(rs1) + register.get(rs2)))
        await s_type(dut, rd, register.get(rd))

    # await r_type(dut, "ADD","x6", "x2", "x3")
    # register.update("x6", register.get("x2") + register.get("x3"))
    # await s_type(dut, "x6", register.get("x6"))


    print("Test SUB\n")
    register.print_all()

    for rd in reg_namelist[1:]:
        imm = randint(-128, 127)
        await l_type(dut, rd, imm)
        register.update(rd, imm)
    register.print_all()

    for i in range(20):
        rd = choice(reg_namelist[1:])
        rs1 = choice(reg_namelist)
        rs2 = choice(reg_namelist)
        await r_type(dut, "SUB", rd, rs1, rs2)
        register.update(rd, to_int(register.get(rs1) - register.get(rs2)))
        await s_type(dut, rd, register.get(rd))

    # await r_type(dut, "SUB","x7", "x2", "x3")
    # register.update("x7", register.get("x2") - register.get("x3"))
    # await s_type(dut, "x7", register.get("x7"))

    print("Test XOR\n")
    register.print_all()

    for rd in reg_namelist[1:]:
        imm = randint(-128, 127)
        await l_type(dut, rd, imm)
        register.update(rd, imm)
    register.print_all()

    rd = choice(reg_namelist[1:])
    rs1 = choice(reg_namelist)
    await r_type(dut, "XOR", rd, rs1, "x0")
    register.update(rd, to_int(register.get(rs1) ^ 0))
    await s_type(dut, rd, register.get(rd))

    await l_type(dut, "x7", -1)
    register.update("x7", -1)
    rd = choice(reg_namelist[1:])
    rs1 = choice(reg_namelist)
    await r_type(dut, "XOR", rd, rs1, "x7")
    register.update(rd, to_int(register.get(rs1) ^ register.get("x7")))
    await s_type(dut, rd, register.get(rd))

    for i in range(10):
        rd = choice(reg_namelist[1:])
        rs1 = choice(reg_namelist)
        rs2 = choice(reg_namelist)
        await r_type(dut, "XOR", rd, rs1, rs2)
        register.update(rd, to_int(register.get(rs1) ^ register.get(rs2)))
        await s_type(dut, rd, register.get(rd))

    # await r_type(dut, "XOR", "x4", "x2", "x3")
    # register.update("x4", register.get("x2") ^ register.get("x3"))
    # await s_type(dut, "x4", register.get("x4"))

    print("Test SLT\n")
    register.print_all()

    for rd in reg_namelist[1:]:
        imm = randint(-128, 127)
        await l_type(dut, rd, imm)
        register.update(rd, imm)
    register.print_all()

    rd = choice(reg_namelist[1:])
    rs1 = choice(reg_namelist)
    await r_type(dut, "SLT", rd, rs1, "x0")
    register.update(rd, to_int(register.get(rs1) < 0))
    await s_type(dut, rd, register.get(rd))

    await l_type(dut, "x7", 127)
    register.update("x7", 127)
    rd = choice(reg_namelist[1:])
    rs1 = choice(reg_namelist)
    await r_type(dut, "SLT", rd, rs1, "x7")
    register.update(rd, to_int(register.get(rs1) < register.get("x7")))
    await s_type(dut, rd, register.get(rd))

    await l_type(dut, "x7", -128)
    register.update("x7", -128)
    rd = choice(reg_namelist[1:])
    rs2 = choice(reg_namelist)
    await r_type(dut, "SLT", rd,"x7", rs2)
    register.update(rd, to_int(register.get("x7") < register.get(rs2)))
    await s_type(dut, rd, register.get(rd))

    for i in range(10):
        rd = choice(reg_namelist[1:])
        rs1 = choice(reg_namelist)
        rs2 = choice(reg_namelist)
        await r_type(dut, "SLT", rd, rs1, rs2)
        register.update(rd, to_int(register.get(rs1) < register.get(rs2)))
        await s_type(dut, rd, register.get(rd))

    # await r_type(dut, "SLT", "x5", "x2", "x3")
    # register.update("x5", (register.get("x2") < register.get("x3")))
    # await s_type(dut, "x5", register.get("x5"))


    print("Test I Type\n")
    print("Test ADDI\n")
    register.print_all()

    for rd in reg_namelist[1:]:
        imm = randint(-128, 127)
        await l_type(dut, rd, imm)
        register.update(rd, imm)
    register.print_all()

    rd = choice(reg_namelist[1:])
    rs1 = choice(reg_namelist)
    await i_type(dut,"ADDI",rd, rs1, 31)
    register.update(rd, to_int(register.get(rs1) + 31))
    await s_type(dut, rd, register.get(rd))

    for i in range(10):
        rd = choice(reg_namelist[1:])
        rs1 = choice(reg_namelist)
        imm = randint(0, 31)
        await i_type(dut, "ADDI", rd, rs1, imm)
        register.update(rd, to_int(register.get(rs1) + imm))
        await s_type(dut, rd, register.get(rd))

    print("Test SUBI\n")
    register.print_all()

    for rd in reg_namelist[1:]:
        imm = randint(-128, 127)
        await l_type(dut, rd, imm)
        register.update(rd, imm)
    register.print_all()

    rd = choice(reg_namelist[1:])
    rs1 = choice(reg_namelist)
    await i_type(dut, "SUBI", rd, rs1, 31)
    register.update(rd, to_int(register.get(rs1) - 31))
    await s_type(dut, rd, register.get(rd))

    for i in range(10):
        rd = choice(reg_namelist[1:])
        rs1 = choice(reg_namelist)
        imm = randint(0, 31)
        await i_type(dut, "SUBI", rd, rs1, imm)
        register.update(rd, to_int(register.get(rs1) - imm))
        await s_type(dut, rd, register.get(rd))

    # await i_type(dut, "SUBI", "x7", "x5", 4)
    # register.update("x7", register.get("x5") - 4)
    # await s_type(dut, "x7", register.get("x7"))

    print("Test SLL\n")
    register.print_all()

    for rd in reg_namelist[1:]:
        imm = randint(-128, 127)
        await l_type(dut, rd, imm)
        register.update(rd, imm)
    register.print_all()

    rd = choice(reg_namelist[1:])
    rs1 = choice(reg_namelist)
    await i_type(dut, "SLL", rd, rs1,0)
    register.update(rd, (to_int(register.get(rs1) << 0)))
    await s_type(dut, rd, register.get(rd))

    rd = choice(reg_namelist[1:])
    rs1 = choice(reg_namelist)
    await i_type(dut, "SLL", rd, rs1, 7)
    register.update(rd, (to_int(register.get(rs1) << 7)))
    await s_type(dut, rd, register.get(rd))

    for i in range(10):
        rd = choice(reg_namelist[1:])
        rs1 = choice(reg_namelist)
        imm = randint(0, 7)
        await i_type(dut, "SLL", rd, rs1, imm)
        register.update(rd, (to_int(register.get(rs1) << imm)))
        await s_type(dut, rd, register.get(rd))

    # await i_type(dut, "SLL", "x1", "x2", 7)
    # register.update("x1", to_int((register.get("x2") << 7) & 0xFF))
    # await s_type(dut, "x1", register.get("x1"))

    print("Test SRL\n")
    register.print_all()

    for rd in reg_namelist[1:]:
        imm = randint(-128, 127)
        await l_type(dut, rd, imm)
        register.update(rd, imm)
    register.print_all()

    rs1 = choice(reg_namelist)
    rd = choice(reg_namelist[1:])
    await i_type(dut, "SRL", rd, rs1, 0)
    register.update(rd, shift_right_logical(register.get(rs1), 0))
    await s_type(dut, rd, register.get(rd))

    rd = choice(reg_namelist[1:])
    await i_type(dut, "SRL", rd, rs1, 7)
    register.update(rd, shift_right_logical(register.get(rs1), 7))
    await s_type(dut, rd, register.get(rd))

    await l_type(dut, "x7", 127)
    register.update("x7", 127)
    # await s_type(dut,"x7", register.get("x7"))

    rd = choice(reg_namelist[1:])
    await i_type(dut, "SRL", rd, "x7", 0)
    register.update(rd, shift_right_logical(register.get("x7"), 0))
    await s_type(dut, rd, register.get(rd))

    rd = choice(reg_namelist[1:])
    await i_type(dut, "SRL", rd, "x7", 7)
    register.update(rd, shift_right_logical(register.get("x7"), 7))
    await s_type(dut, rd, register.get(rd))

    await l_type(dut, "x7", -128)
    register.update("x7", -128)
    # await s_type(dut,"x7", register.get("x7"))

    rd = choice(reg_namelist[1:])
    await i_type(dut, "SRL", rd, "x7", 0)
    register.update(rd, shift_right_logical(register.get("x7"), 0))
    await s_type(dut, rd, register.get(rd))

    rd = choice(reg_namelist[1:])
    await i_type(dut, "SRL", rd, "x7", 7)
    register.update(rd, shift_right_logical(register.get("x7"), 7))
    await s_type(dut, rd, register.get(rd))

    for i in range(10):
        rd = choice(reg_namelist[1:])
        rs1 = choice(reg_namelist)
        imm = randint(0, 7)
        await i_type(dut, "SRL", rd, rs1, imm)
        register.update(rd, shift_right_logical(register.get(rs1), imm))
        await s_type(dut, rd, register.get(rd))

    # await i_type(dut, "SRL", "x1", "x7", 1)
    # register.update("x1", shift_right_logical(register.get("x7"), 1))
    # await s_type(dut, "x1", register.get("x1"))
    #
    # await i_type(dut, "SRL", "x1", "x2", 3)
    # register.update("x1", shift_right_logical(register.get("x2"), 3))
    # await s_type(dut, "x1", register.get("x1"))

    print("Test SRA\n")
    register.print_all()

    for rd in reg_namelist[1:]:
        imm = randint(-128, 127)
        await l_type(dut, rd, imm)
        register.update(rd, imm)
    register.print_all()

    rs1 = choice(reg_namelist)
    rd = choice(reg_namelist[1:])
    await i_type(dut, "SRA", rd, rs1, 0)
    register.update(rd, to_int(register.get(rs1) >> 0))
    await s_type(dut, rd, register.get(rd))

    rs1 = choice(reg_namelist)
    await i_type(dut, "SRA", rd, rs1, 7)
    register.update(rd, to_int(register.get(rs1) >> 7))
    await s_type(dut, rd, register.get(rd))

    await l_type(dut, "x7", 127)
    register.update("x7", 127)
    # await s_type(dut,"x7", register.get("x7"))

    await i_type(dut, "SRA", rd, "x7", 0)
    register.update(rd, to_int(register.get("x7") >> 0))
    await s_type(dut, rd, register.get(rd))

    await i_type(dut, "SRA", rd, "x7", 7)
    register.update(rd, to_int(register.get("x7") >> 7))
    await s_type(dut, rd, register.get(rd))

    await l_type(dut, "x7", -128)
    register.update("x7", -128)
    # await s_type(dut, "x7", register.get("x7"))

    await i_type(dut, "SRA", rd, "x7", 0)
    register.update(rd, to_int(register.get("x7") >> 0))
    await s_type(dut, rd, register.get(rd))

    await i_type(dut, "SRA", rd, "x7", 7)
    register.update(rd, to_int(register.get("x7") >> 7))
    await s_type(dut, rd, register.get(rd))

    for i in range(10):
        rd = choice(reg_namelist[1:])
        rs1 = choice(reg_namelist)
        imm = randint(0, 7)
        await i_type(dut, "SRA", rd, rs1, imm)
        register.update(rd, to_int(register.get(rs1) >> imm))
        await s_type(dut, rd, register.get(rd))

    # await i_type(dut, "SRA", "x1", "x7", 4)
    # register.update("x1", (register.get("x7") >> 4))
    # await s_type(dut, "x1", register.get("x1"))

    print("Test B-Type\n")
    print("Test BEQ\n")
    register.print_all()

    await l_type(dut, "x1", 3)
    register.update("x1", 3)
    await l_type(dut, "x2", 3)
    register.update("x2", 3)
    await l_type(dut, "x3", -128)
    register.update("x3", -128)
    await l_type(dut, "x4", 127)
    register.update("x4", 127)
    for rd in reg_namelist[5:]:
        imm = randint(-128, 127)
        await l_type(dut, rd, imm)
        register.update(rd, imm)
    register.print_all()


    await b_type(dut, "BEQ", "x1", "x2", (register.get("x1") == register.get("x2")))

    await b_type(dut, "BEQ", "x2", "x3", (register.get("x2") == register.get("x3")))

    for i in range(10):
        rs1 = choice(reg_namelist)
        rs2 = choice(reg_namelist)
        await b_type(dut, "BEQ", rs1, rs2, (register.get(rs1) == register.get(rs2)))


    print("Test BNE\n")
    register.print_all()

    await b_type(dut, "BNE", "x1", "x3", (register.get("x1") != register.get("x3")))

    await b_type(dut, "BNE", "x1", "x2", (register.get("x1") != register.get("x2")))

    for i in range(10):
        rs1 = choice(reg_namelist)
        rs2 = choice(reg_namelist)
        await b_type(dut, "BNE", rs1, rs2, (register.get(rs1) != register.get(rs2)))

    print("Test BLT\n")
    register.print_all()

    await b_type(dut, "BLT", "x3", "x2", (register.get("x3") < register.get("x2")))

    await b_type(dut, "BLT", "x1", "x2", (register.get("x1") < register.get("x2")))

    for i in range(10):
        rs1 = choice(reg_namelist)
        rs2 = choice(reg_namelist)
        await b_type(dut, "BLT", rs1, rs2, (register.get(rs1) < register.get(rs2)))

    print("\nAll Tests Passed!\n\n")
