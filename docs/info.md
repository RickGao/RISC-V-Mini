<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This project aims to design and implement a compact 8-bit RISC-V processor core optimized for Tiny Tapeout, a fabrication platform for small-scale educational IC projects. The processor employs a customized, compressed RISC-V instruction set (RVC) to reduce instruction width, leading to a more compact design suited to Tiny Tapeout's area and resource constraints. Developed in Verilog, this processor will handle computational, load/store, and control-flow operations efficiently and undergo verification through simulation and testing.

Processor Components
The processor comprises the following core components, optimized to meet Tiny Tapeout’s area requirements:

1. Control Unit
Generates control signals for instruction execution based on opcode and other instruction fields.
2. Register File
Contains 8 general-purpose, 8-bit-wide registers. Register R0 will always return zero when read, adhering to RISC-V convention.
3. Arithmetic Logic Unit (ALU)
Performs basic arithmetic (addition, subtraction) and logical (AND, OR, XOR, SLT) operations as specified by the decode stage. Supports custom compressed RISC-V instructions.
4. Datapath
Single-cycle execution, optimized for minimal hardware complexity, reducing the processor’s area and power consumption.

## How to test

Test with Tiny Tapeout flow

## External hardware

No External Hardware
