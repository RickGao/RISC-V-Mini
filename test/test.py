# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_register_file(dut):
    dut._log.info("Start register file test")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset the design
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Test write and read operations
    dut._log.info("Testing write and read operations")

    # Write value to register 1
    dut.uio_in.value = 0b10000010  # IO[7]=1 (we=1), IO[6:4]=001 (write to reg 1), IO[3:0]=0b0010 (data=2)
    await ClockCycles(dut.clk, 1)

    # Read back value from register 1
    dut.ui_in.value = 0b00000001  # Input[2:0]=001 (read reg 1)
    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value[3:0] == 2, f"Expected register 1 to contain 2, got {dut.uo_out.value[3:0]}"

    # Write value to register 2
    dut.uio_in.value = 0b10000101  # IO[7]=1 (we=1), IO[6:4]=010 (write to reg 2), IO[3:0]=0b0101 (data=5)
    await ClockCycles(dut.clk, 1)

    # Read back value from register 2
    dut.ui_in.value = 0b00000100  # Input[6:4]=010 (read reg 2)
    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value[7:4] == 5, f"Expected register 2 to contain 5, got {dut.uo_out.value[7:4]}"

    # Write and read to ensure register 0 remains 0 (RISC-V convention)
    dut.uio_in.value = 0b10000011  # IO[7]=1 (we=1), IO[6:4]=000 (write to reg 0), IO[3:0]=0b0011 (attempt to write 3)
    await ClockCycles(dut.clk, 1)

    # Check that register 0 is still zero
    dut.ui_in.value = 0b00000000  # Input[2:0]=000 (read reg 0)
    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value[3:0] == 0, f"Expected register 0 to remain 0, got {dut.uo_out.value[3:0]}"

    dut._log.info("Register file test completed successfully")
