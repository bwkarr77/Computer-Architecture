"""CPU functionality."""
# to run in terminal, type: py ls8.py examples/mult.ls8

import sys

# from print8.ls8:
LOAD    = 0b10000010    # LOAD
PRINT   = 0b01000111    # PRINT
HALT    = 0b00000001    # HALT
MULT    = 0b10100010    # MULTIPLY NUMBERS TOGETHER
PUSH    = 0b01000101    # PUSH ONTO STACK
POP     = 0b01000110    # POP OFF THE STACK
ADD     = 0b10100110    # ADD NUMBERS TOGETHER
CALL    = 0b01010000    # CALL
RET     = 0b00010001    # RET

OP1     = 0b10101010
OP2     = 0b11110000


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256  # 256 bytes of RAM/memory
        self.registers = [0] * 8  # registers 0:7 are saved for quick access
        self.registers[7] = 0xF4  # 244
        self.pc = 0  # program counter/pointer

        # ____Branch Tables____
        self.branchtable = {}
        self.branchtable[LOAD] = self.ldi
        self.branchtable[PRINT] = self.prn
        self.branchtable[HALT] = self.hlt
        self.branchtable[MULT] = self.mul
        self.branchtable[PUSH] = self.push
        self.branchtable[POP] = self.pop
        self.branchtable[ADD] = self.add
        self.branchtable[CALL] = self.call
        self.branchtable[RET] = self.ret

    def load(self):
        """Load a program into memory."""

        # address = 0
        # For now, we've just hardcoded a program:
        # program = [
        #     # From print8.ls8
        #     0b10000010, # LOAD R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRINT R0
        #     0b00000000,
        #     0b00000001, # HALT
        # ]
        #
        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        if len(sys.argv) != 2:
            print("Usage: py ls8.py <filename.py>")
            sys.exit(1)

        address = 0
        try:
            with open(sys.argv[1]) as f:
                # print(sys.argv)  # sys.argv = ['ls8.py', 'examples/<filename>']
                for line in f:
                    # separate each line into the binary code from the file
                    code_number = line.split('#')[0].strip()   # ex: 100000010
                    code_number = line[:line.find('#')]

                    if code_number == "":
                        continue  # skips to the next iteration

                    try:
                        code_number = int(code_number, 2)

                    except ValueError:
                        print(f"Invalid Number: {code_number}")
                        sys.exit(1)

                    self.ram_write(address, code_number)
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[1]} file not found")
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.registers[reg_a] += self.registers[reg_b]
        #elif op == "SUB": etc
        elif op == "MULT":
            self.registers[reg_a] *= self.registers[reg_b]
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
            print(" %02X" % self.registers[i], end='')

        print()

    def ram_read(self, MAR):
        # MAR (Memory Address Register) = address this is read/written to
        # print('ram_read: ', self.ram[MAR])
        # returns the data that is stored inside RAM at the MAR (memory access) location (typically pc)
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        # MAR (Memory Address Register) = address this is read/written to
        # MDR (Memory Data Register) = data to read/write
        self.ram[MAR] = MDR

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            # Instruction Register (IR) is where we store the result from ram_read
            IR = self.ram_read(self.pc)  # should be the "command"/instructions

            num_args = IR >> 6  # returns 2 for commands>2 digits, 1 for commands>1 digit, 0 for commands==1 digit

            try:
                self.branchtable[IR]()
            except KeyError:
                print(f'KeyError at {self.registers[IR]}')
                sys.exit(1)


            if IR == HALT:  # HALT/exit loop
                running = False
                # self.pc += 1

            elif IR == PRINT:  # PRINT the register
                reg_idx = self.ram_read(self.pc + 1)
                print(self.registers[reg_idx])
                self.pc += 1
                # self.pc += 2

            elif IR == LOAD:  # LOAD
                # get the register index (pc + 1) and the value (pc + 2)
                reg_idx = self.ram_read(self.pc + 1)
                value = self.ram_read(self.pc + 2)

                # save the value into the correct register
                self.registers[reg_idx] = value
                self.pc += 2
                # self.pc += 3

            elif IR == ADD:
                # pull out arguments
                reg_idx_1 = self.ram_read(self.pc + 1)
                reg_idx_2 = self.ram_read(self.pc + 2)

                # add register 2 to register 1
                self.registers[reg_idx_1] = self.registers[reg_idx_1] + self.registers[reg_idx_2]
                self.pc += 2

            elif IR == MULT:
                # pull out arguments
                reg_idx_1 = self.ram_read(self.pc + 1)
                reg_idx_2 = self.ram_read(self.pc + 2)

                self.registers[reg_idx_1] *= self.registers[reg_idx_2]
                self.pc += 2
                # self.pc += 3
                # print('7: ', self.registers[7])

            elif IR == PUSH:
                # **SP = Stack Pointer
                # 1. Decrement the 'SP'
                self.registers[7] -= 1  # decrement the 'SP' by 1

                # 2. Copy the value in the given register to the address pointed to by "SP"
                reg_idx = self.ram_read(self.pc + 1)
                value = self.registers[reg_idx]

                # 3. SP = registers[7]
                # memory[SP] = value
                SP = self.registers[7]
                self.ram_write(SP, value)

                self.pc += 1

            elif IR == POP:
                # 1. Copy the value from the address pointed to by "SP" to given register
                # address of SP, its value at the address, and the register idx
                SP = self.registers[7]
                value = self.ram_read(SP)
                reg_idx = self.ram_read(self.pc + 1)

                # place value into the register idx
                self.registers[reg_idx] = value

                self.registers[7] += 1

                # self.pc += 1

            elif IR == RET:
                print('elif RET')
                SP = self.registers[7]
                return_address = self.ram[SP]

                self.pc = return_address

                self.registers[7] += 1

            elif IR == CALL:
                # # save the register (aka 'spot') to "return" back to after CALL
                # reg_idx = self.ram_read(self.pc + 1)
                # # print('elif CALL: ', self.pc+1, reg_idx, self.registers)
                #
                # #
                # self.registers[7] -= 1
                # # SP = self.registers[7]
                #
                # self.ram[self.registers[7]] = self.pc + 2
                #
                # # print('test: ', reg_idx, self.registers, self.registers[1])
                # # self.pc += self.registers[reg_idx]
                # self.pc += 1

                # lesson...
                # save the return address
                return_address = self.pc + 2  # supposed to be pc+2, but there's the auto pc+1

                # push command address after CALL onto stack
                # 1. decrement the SP, then store the value at address
                self.registers[7] -= 1
                # 2. get address, and store return_address at SP address:
                SP = self.registers[7]
                self.ram_write(SP, return_address)

                # retrieve address from register
                reg_idx = self.pc + 1
                # look into register to find address
                subroutine_address = self.registers[reg_idx]

                self.pc = subroutine_address

            else:
                print('else: ', IR)
                sys.exit()

            # skip this IF setting pc directly:
            sets_pc_directly = ((IR >> 4) & 0b0001) == 1
            if not sets_pc_directly:
                self.pc += 1
            # self.pc += num_args

    def handle_op1(self, a):
        print("op 1: " + a)

    def handle_op2(self, a):
        print("op 2: " + a)

    # Branch Table Commands

    def ldi(self):
        print('ldi')

    def prn(self):
        print('prn')

    def hlt(self):
        print('hlt')

    def add(self):
        print('add')

    def mul(self):
        print('mul')

    def push(self):
        print('push')

    def pop(self):
        print('pop')

    def call(self):
        print('call')

    def ret(self):
        print('ret')
