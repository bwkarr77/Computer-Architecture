PRINT_TIM       = 0b00000001
HALT            = 0b00000010
PRINT_NUM       = 0b00000011
SAVE            = 0b00000100
PRINT_REGISTER  = 0b00000101
ADD             = 0b00000110

#SAVE into R2
memory = [
    PRINT_TIM,
    PRINT_NUM,
    42,
    PRINT_TIM,
    PRINT_NUM,
    42,
    PRINT_TIM,
    PRINT_NUM,
    42,
    SAVE,
    2,      # into R2
    99,     # this number
    ADD,
    2,
    3,
    PRINT_REGISTER,
    2,
    HALT
]

registers = [0] * 8


pc = 0
running = True

while running:
    command = memory[pc]
    # print('c: ', command, PRINT_NUM)

    if command == PRINT_TIM:
        print('tim!')

    elif command == PRINT_NUM:
        pc += 1
        number = memory[pc]
        print(number)

    elif command == HALT:
        running = False

    elif command == SAVE:
        reg_idx = memory[pc + 1]
        value = memory[pc + 2]

        # place value into register
        registers[reg_idx] = value

        pc += 2

    elif command == PRINT_REGISTER:
        reg_idx = memory[pc+1]

        # pointer to a register
        print(registers[reg_idx])

        pc += 1

    elif command == ADD:
        # pull out arguments
        reg_idx_1 = memory[pc + 1]
        reg_idx_2 = memory[pc + 2]

        registers[reg_idx_1] = registers[reg_idx_1] + registers[reg_idx_2]

        pc += 2

    else:
        print('unknown command')

    pc += 1

