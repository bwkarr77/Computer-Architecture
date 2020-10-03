"""CPU functionality."""

import sys

# from print8.ls8:
LDI = 0b10000010    # LOAD
PRN = 0b01000111    # PRINT
HLT = 0b00000001    # HALT
MUL = 0b10100010    # MULTIPLY


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256  # 256 bytes of RAM
        self.reg = [0] * 8  #
        self.pc = 0  # program counter

    def load(self):
        """Load a program into memory."""

        # address = 0
        #
        # # For now, we've just hardcoded a program:
        #
        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]
        #
        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        if len(sys.argv) != 2:
            print("Usage: ls8.py filename")
            sys.exit(1)

        try:
            address = 0
            with open(sys.argv[1]) as f:
                for line in f:
                    split_line = line.split('#')
                    code_val = split_line[0].strip()

                    if code_val == "":
                        continue

                    try:
                        code_val = int(code_val, 2)

                    except ValueError:
                        print(f"Invalid Number: {code_val}")
                        sys.exit(1)

                    self.ram_write(address, code_val)
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[1]} file not found")
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, MAR):
        # MAR (Memory Address Register) = address this is read/written to
        print(self.ram[MAR])
        # returns the data that is stored inside RAM at the MAR (memory access) location (typically pc)
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        # MAR (Memory Address Register) = address this is read/written to
        # MDR (Memory Data Register) = data to read/write
        self.ram[MAR] = MDR

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            # Instruction Register (IR) is where we store the result from ram_read
            IR = self.ram_read(self.pc)

            # read and save the bytes from the next 2 RAM locations after pc location.
            # *pc is the 'starting' point/signal, and the next 2 are the data we want to utilize
            op_1 = self.ram_read(self.pc + 1)
            op_2 = self.ram_read(self.pc + 1)

            if IR == HLT:  # HALT/exit loop
                running = False

            elif IR == PRN:  # PRINT the register
                print(self.reg[op_1])
                self.pc += 1

            elif IR == LDI:  # LOAD
                self.reg[op_1] = op_2
                self.pc += 2

            else:
                print('unknown command')

            self.pc += 1
