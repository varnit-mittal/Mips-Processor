import sys

instMem = []
clock = 1
pc = 0
file=''

f = open("./mipsCode.txt", "r")
for line in f:
    instMem.append(line.strip())
f.close()

instr = ''

IfId = {}
IdEx = {}
ExMem = {}
MemWb = {}

ExMem['writeport']=-1
ExMem['Aluresult']=0

IdEx['reg2']=-1
IdEx['memrd']=0

MemWb['pc']=0
MemWb['pcsrc']=-1
MemWb['memrd']=0

dataMem = {}

writeport = 0
Aluresult = 0
zero = -1

regdst = False
alusrc = False
mem2reg = False
regwr = False
memrd = False
memwr = False
branch = False
aluop1 = False
aluop0 = False
jmp = False
pcsrc = False

RegFile = {}
for i in range(32):
    RegFile[i] = 0


def hazardDetection(rt, rs):
    """
    Detects data hazards (load word and store word) hazrds in the pipeline.

    Args:
    rt (int): The destination register of the instruction in the current stage.
    rs (int): The source register of the instruction in the current stage.

    Returns:
    bool: True if there is a data hazard, False otherwise.
    """
    if(IdEx['memrd'] and (IdEx['reg2']==rt or IdEx['reg2']==rs)):
        return True
    else:
        return False

def twos_complement(binary_str):
    """
    Returns the two's complement of a binary string.

    Args:
    binary_str (str): A binary string.

    Returns:
    str: The two's complement of the binary string.
    """
    inverted_str = ''.join(['1' if bit == '0' else '0' for bit in binary_str])

    carry = 1
    result = ''
    for bit in reversed(inverted_str):
        if bit == '0' and carry == 1:
            result = '1' + result
            carry = 0
        elif bit == '1' and carry == 1:
            result = '0' + result
        else:
            result = bit + result

    if(result[0] == "1"):
        return "0"+result[1:]
    else:
        return "1"+result[1:]


def fetch(pc):
    """
    Fetches the instruction from the instruction memory at the given program counter (pc) and stores it in the instruction register (IfId['instruction']).
    Also updates the program counter (IfId['pc']) to point to the next instruction.

    Args:
    pc (int): The program counter value.

    Returns:
    None
    """
    if(pc>=len(instMem) or pc<0):
        return
    instr = instMem[pc]
    IfId['pc'] = pc+1
    IfId['instruction'] = instr


def contol_signals_decoder(opcode,funct):
    """
    Decodes the opcode and sets the control signals for the processor.

    Args:
    opcode: A string representing the opcode.

    Returns:
    None
    """
    v = opcode
    regdst = (not int(v[2])) and (not int(v[3])) and (not int(v[4]))
    alusrc = int(v[2]) or int(v[5])
    mem2reg = not(int (v[2])) and int(v[5])
    regwr = (not int(v[3]) and (not int(v[4]))) or (not int(v[2]) and int(v[5]))
    memrd = not int(v[2]) and int(v[5])
    memwr = int(v[2]) and int(v[5])
    branch = int(v[3])
    aluop1 = (not int(v[0]) and (not int(v[3])))
    aluop0 = int(v[3])
    jmp = not int(v[0]) and int(v[4])

    if(funct=="100010"):
        IdEx['Aluinp']=1
    elif(funct=="101010"):
        IdEx['Aluinp']=2
    else:
        IdEx['Aluinp']=0

    IdEx['regdst'] = regdst
    IdEx['alusrc'] = alusrc
    IdEx['mem2reg'] = mem2reg
    IdEx['regwr'] = regwr
    IdEx['memrd'] = memrd
    IdEx['memwr'] = memwr
    IdEx['branch'] = branch
    IdEx['aluop1'] = aluop1
    IdEx['aluop0'] = aluop0
    IdEx['jmp'] = jmp
    IdEx['Hazard']=False
    global zero
    zero=-1

def decode(inst):
    """
    Decodes the given instruction and sets the control signals and register values in the IdEx pipeline register.

    Args:
    inst (str): 32-bit binary string representing the instruction to be decoded.

    Returns:
    None
    """
    global clock 
    opcode = inst[0:6]
    rs = inst[6:11]
    rt = inst[11:16]
    rd = inst[16:21]
    shamt = inst[21:26]
    funct = inst[26:32]
    imm = inst[16:32]
    addr = inst[6:32]

    if(hazardDetection(int(rt,2),int(rs,2)) and MemWb['pc']!=IdEx['pc'] and len(instMem)!=1):
        IdEx['Hazard']=True
        clock+=1

    contol_signals_decoder(opcode,funct)

    if(IdEx['regdst']):
        writeport = int(rd, 2)
    else:
        writeport = int(rt, 2)

    if(imm[0]=="1"):
        st = twos_complement(imm)
    else:
        st=imm
    k = int(st[1:], 2)
    if(st[0] == "1"):
        k = -k

    addr = "0000"+addr+"00"
    add1 = int((int(addr, 2)-0x00400000)/4)
    IdEx['reg1'] = int(rs, 2)
    IdEx['reg2'] = int(rt, 2)
    IdEx['pc'] = IfId['pc']
    IdEx['offset'] = k
    IdEx['address'] = add1
    IdEx['writeport'] = writeport

    fetch(IfId['pc'])

def execute():

    """
    Executes the instruction in the Ex stage of the pipeline and updates the Ex/Mem pipeline register accordingly.
    """

    reg1 = IdEx['reg1']
    reg2 = IdEx['reg2']
    offset = IdEx['offset']
    p1 = IdEx['pc']

    if(ExMem['writeport']==IdEx['reg1'] and len(instMem)!=1):
        if IdEx['alusrc']:
            Aluresult = ExMem['Aluresult']+offset
        else:
            Aluresult = ExMem['Aluresult']+RegFile[reg2]
        
        if(IdEx['branch']):
            zero = ExMem['Aluresult']-RegFile[reg2]
            ExMem['zero']=zero

        if(IdEx['Aluinp']==1):
            Aluresult = ExMem['Aluresult']-RegFile[reg2]

        elif(IdEx['Aluinp']==2):
            if(ExMem['Aluresult']<RegFile[reg2]):
                Aluresult=1
            else:
                Aluresult=0
    
    elif(ExMem['writeport']==IdEx['reg2'] and len(instMem)!=1):
        if IdEx['alusrc']:
            Aluresult = RegFile[reg1]+offset
        else:
            Aluresult = RegFile[reg1]+ExMem['Aluresult']

        if(IdEx['branch']):
            zero = RegFile[reg1]-ExMem['Aluresult']
            ExMem['zero']=zero

        if(IdEx['Aluinp']==1):
            Aluresult = RegFile[reg1]-ExMem['Aluresult']
        elif(IdEx['Aluinp']==2):
            if(RegFile[reg1]<ExMem['Aluresult']):
                Aluresult=1
            else:
                Aluresult=0 

    else:
        if IdEx['alusrc']:
            Aluresult = RegFile[reg1]+offset
        else:
            Aluresult = RegFile[reg1]+RegFile[reg2]
        
        if(IdEx['branch']):
            zero = RegFile[reg1]-RegFile[reg2]
            ExMem['zero']=zero

        if(IdEx['Aluinp']==1):
            Aluresult = RegFile[reg1]-RegFile[reg2]

        elif(IdEx['Aluinp']==2):
            if(RegFile[reg1]<RegFile[reg2]):
                Aluresult=1
            else:
                Aluresult=0
          
    if(MemWb['memrd'] and len(instMem)!=1):
        if(MemWb['writeport']==reg1):
            if IdEx['alusrc']:
                Aluresult = MemWb['MemOut']+offset
            else:
                Aluresult = MemWb['MemOut']+RegFile[reg2]
            
            if(IdEx['branch']):
                zero = MemWb['MemOut']-RegFile[reg2]
                ExMem['zero']=zero

            if(IdEx['Aluinp']==1):
                Aluresult = MemWb['MemOut']-RegFile[reg2]
            elif(IdEx['Aluinp']==2):
                if(MemWb['MemOut']<RegFile[reg2]):
                    Aluresult=1
                else:
                    Aluresult=0

        elif(MemWb['writeport']==reg2):
            if IdEx['alusrc']:
                Aluresult = RegFile[reg1]+offset
            else:
                Aluresult = RegFile[reg1]+MemWb['MemOut']

            if(IdEx['branch']):
                zero = RegFile[reg1]-MemWb['MemOut']
                ExMem['zero']=zero

            if(IdEx['Aluinp']==1):
                Aluresult = RegFile[reg1]-MemWb['MemOut']
            elif(IdEx['Aluinp']==2):
                if(RegFile[reg1]<MemWb['MemOut']):
                    Aluresult=1
                else:
                    Aluresult=0

    pcsrc = IdEx['branch'] and (not zero)

    ExMem['pcsrc'] = pcsrc
    if(pcsrc):
        pc = p1+offset
    else:
        pc = p1

    if(IdEx['jmp']):
        pc = IdEx['address']

    ExMem['pc'] = pc
    ExMem['Aluresult'] = Aluresult
    ExMem['reg2'] = reg2
    ExMem['regdst'] = IdEx['regdst']
    ExMem['alusrc'] = IdEx['alusrc']
    ExMem['mem2reg'] = IdEx['mem2reg']
    ExMem['regwr'] = IdEx['regwr']
    ExMem['memrd'] = IdEx['memrd']
    ExMem['memwr'] = IdEx['memwr']
    ExMem['branch'] = IdEx['branch']
    ExMem['aluop1'] = IdEx['aluop1']
    ExMem['aluop0'] = IdEx['aluop0']
    ExMem['jmp'] = IdEx['jmp']
    ExMem['writeport'] = IdEx['writeport']
    decode(IfId['instruction'])

def memory():
    """
    This function performs memory operations based on the input flags from the ExMem stage.
    It reads from or writes to the data memory based on the memrd and memwr flags respectively.
    It updates the MemWb register with the appropriate values for the next stage.
    If the pcsrc or jmp flags are set, it returns without executing the next stage.
    """
    mem_out = 0
    if(ExMem['memrd']):
        mem_out = dataMem[ExMem['Aluresult']]
    if(ExMem['memwr']):
        dataMem[ExMem['Aluresult']] = RegFile[ExMem['reg2']]

    MemWb['AluResult'] = ExMem['Aluresult']
    MemWb['MemOut'] = mem_out

    MemWb['pc'] = ExMem['pc']
    MemWb['pcsrc']=ExMem['pcsrc']
    MemWb['regdst'] = ExMem['regdst']
    MemWb['alusrc'] = ExMem['alusrc']
    MemWb['mem2reg'] = ExMem['mem2reg']
    MemWb['regwr'] = ExMem['regwr']
    MemWb['memrd'] = ExMem['memrd']
    MemWb['memwr'] = ExMem['memwr']
    MemWb['branch'] = ExMem['branch']
    MemWb['aluop1'] = ExMem['aluop1']
    MemWb['aluop0'] = ExMem['aluop0']
    MemWb['jmp'] = ExMem['jmp']
    MemWb['writeport'] = ExMem['writeport']

    if(MemWb['pcsrc'] or MemWb['jmp']):
        return
    execute()

def writeback():
    """
    Writes the data back to the register file if MemWb['regwr'] is True.
    If MemWb['mem2reg'] is True, writes MemWb['MemOut'] to the register file at MemWb['writeport'].
    Otherwise, writes MemWb['AluResult'] to the register file at MemWb['writeport'].
    Calls memory() function.
    """
    if(MemWb['regwr']):
        if(MemWb['mem2reg']):
            RegFile[MemWb['writeport']] = MemWb['MemOut']
        else:
            RegFile[MemWb['writeport']] = MemWb['AluResult']
    memory()

def main():
    """
    Executes the instructions in the instruction memory and writes the output to a file.
    The output file name is provided as a command line argument.
    The function also prints the number of clock cycles, registers with non-zero values, and data memory locations with non-zero values.
    """

    dataMem[0]=9
    dataMem[1]=7
    dataMem[2]=3
    dataMem[3]=15
    dataMem[4]=1
    dataMem[5]=99
    dataMem[6]=10
    dataMem[7]=6
    dataMem[8]=1
    global file
    global pc
    global clock
    try:
        file=sys.argv[1]
    except Exception as e:
        raise Exception("Please provide an output file name") from e
    
    f=open(file,"w")
    while(pc<len(instMem)):
        pc=MemWb['pc']
        temp=pc
        if(pc>=len(instMem) or pc<0):
            break
        fetch(pc)
        clock+=1
        decode(IfId['instruction'])
        clock+=1
        execute()
        clock+=1
        memory()
        clock+=1
        writeback()

        if(not MemWb['pcsrc'] or not MemWb['jmp'] and pc>0):
            for i in range(len(instMem)-1-temp):
                if(MemWb['pcsrc'] or MemWb['jmp']):
                    break
                clock+=1
                writeback()

    
    f.write(f"No. of clock cycles are: {clock}\n")
    f.write("The Registers with non-zero values are:\n")
    for i in range(32):
        if(RegFile[i]!=0):
            f.write(f"${i} = {RegFile[i]}\n")

    f.write("The Data Memory locaations with non-zero values are:\n")
    for x in dataMem:
        f.write(f"dataMem[{x}] = {dataMem[x]}\n")
    
    f.close()

if __name__=="__main__":
    main()