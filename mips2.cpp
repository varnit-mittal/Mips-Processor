/*This is a simple implementation of a non-pipelined MIPS processor, which takes machine code from a file as input and
executes the program. Supported instructions are lw,sw,add,addi,sub,beq,slt and jump.
All assumptions made are given in the report.

-IMT2022076 Mohit Naik
*/

#include<bits/stdc++.h>
using namespace std;
vector<string> instr_mem; //MIPS Instruction Memory
vector<int> data_mem(1000); //MIPS Data Memory (100 locations)
vector<int> reg_file(32,0); //MIPS Register File
vector<string> regs = {"$zero","$at","$v0","$v1","$a0","$a1","$a2","$a3","$t0","$t1","$t2","$t3","$t4","$t5",
"$t6","$t7","$s0","$s1","$s2","$s3","$s4","$s5","$s6","$s7","$t8","$t9","$k0","$k1","$gp","$sp","$fp","$ra"}; //register set
int PC = 0, writeport=0, ALUinp, ALUresult=0, clk=0; //program counter, reg writeport, ALU control, ALU result and clock
bool regdst,alusrc,mem2reg,regwr,memrd,memwr,branch,jmp,pcsrc,zero; //The MIPS control signals

//The 5 stages of an instruction
void fetch(int i);
void decode(string s);
void execute(string rs,string rt,string imm, string op);
void mem_access(string rt);
void writeback(int mem_out);

void set_control_signals(string op,string fun){ //sets the appropriate control signals based on the opcode and function fields
    vector<bool> v;
    for(auto i:op) v.push_back(atoi(&i));
    regdst = !v[2] && !v[3] && !v[4];
    alusrc = v[2] || v[5];
    mem2reg = !v[2] && v[5];
    regwr = (!v[3] && !v[4]) || (!v[2] && v[5]);
    memrd = !v[2] && v[5];
    memwr = v[2] && v[5];
    branch = v[3];
    jmp = !v[0] && v[4];
    if (op=="000000"){
        if(fun=="100000") ALUinp = 0;
        else if(fun=="100010") ALUinp = 1;
        else if(fun=="101010") ALUinp = 2;
    }
    else ALUinp = 0;
}

int bin_to_int(string s){ //returns decimal equivalent of a binary string
    return stoi(s,nullptr,2);
}

int twoscomp(string &s) { //returns decimal equivalent of a signed 2's complement binary string
    int ans=0,n = s.size();
    if (s[0]=='1'){
        for (int i=1;i<n;i++) s[i]=(s[i]=='0') ? '1' : '0';
        for (int i=n-1;i>=0;i--){
            if (s[i]=='0'){
                s[i]='1';
                break;
            } 
            else s[i]='0';
        }
    }
    for (int i=1;i<n;i++) if (s[i] == '1') ans+=(1<<(n-1-i));
    return (s[0]=='1') ? -ans : ans;
}

void fetch(int i){ //fetches the ith instruction from instruction memory
    string instr = instr_mem[i];
    // if(PC==8)
    // cout << "INSTRUCTION = " << instr << endl;
    clk++;
    decode(instr);
}

void decode(string s){ //decodes the instruction into its components, and sets the control signals
    string op = s.substr(0,6); //opcode
    string s1 = s.substr(6,5); //rs
    string s2 = s.substr(11,5); //rt
    string s3 = s.substr(16,5); //rd
    string s4 = s.substr(21,5); //shamt
    string s5 = s.substr(26,6); //func
    set_control_signals(op,s5);
    writeport=regdst ? bin_to_int(s3) : bin_to_int(s2); //decides which is the destination register
    clk++;
    execute(s1,s2,s3+s4+s5,op);
}

void execute(string rs,string rt,string imm,string op){ //executes the appropriate instruction
    // cout << "Value of $t3 = " << reg_file[11] << endl;
    if(ALUinp==0){
        ALUresult = alusrc ? reg_file[bin_to_int(rs)]+twoscomp(imm) : reg_file[bin_to_int(rs)]+reg_file[bin_to_int(rt)];
    }
    else if(ALUinp==1) ALUresult = reg_file[bin_to_int(rs)]-reg_file[bin_to_int(rt)];
    else if(ALUinp==2)
    {
        // cout <<  "rs = " <<bin_to_int(rs) << " rt = "<< bin_to_int(rt) << endl;
        // cout << "Value in rs = " << reg_file[bin_to_int(rs)] << " Value in rt = "<< reg_file[bin_to_int(rt)] << " My writeport = " << writeport << endl;
        if((reg_file[bin_to_int(rs)]<reg_file[bin_to_int(rt)]))
            ALUresult=1;
        else
            ALUresult=0;
    }
    zero = (reg_file[bin_to_int(rs)]==reg_file[bin_to_int(rt)]);
    // if(zero==1 && branch)
    // {
    //     cout << "I am seeing the branch instruction \n";
    //     cout << "rs = " <<bin_to_int(rs) << " rt = "<< bin_to_int(rt) << endl;
    //     cout << "Value in rs = " << reg_file[bin_to_int(rs)] << " Value in rt = "<< reg_file[bin_to_int(rt)] << endl;
    // }
    pcsrc = zero && branch;
    PC = pcsrc ? PC+1+twoscomp(imm) : PC+1; //decides what is the next value of PC
    if (jmp) 
    {
        PC = bin_to_int(rs+rt+imm);
        // cout << PC << endl;
    }; //Handles the jump instruction
    clk++;
    // cout<<"Clock cycle number = "<<clk<<"\n";
    // cout<<"Program counter location = "<<PC<<"\n";
    // cout<<"Nonzero registers :\n";
    // for(int i=0;i<32;i++) if(reg_file[i]) cout<<regs[i]<<" = "<<reg_file[i]<<"\n";
    // cout<<"Nonzero data memory locations :\n";
    // for(int i=0;i<100;i++) if(data_mem[i]) cout<<i<<" : "<<data_mem[i]<<"\n";
    mem_access(rt);
}

void mem_access(string rt){ //reads from or writes to memory
    int mem_out = 0;
    if(memrd) mem_out = data_mem[ALUresult]; //for the lw instruction
    if(memwr) data_mem[ALUresult] = reg_file[bin_to_int(rt)]; //for the sw instruction
    clk++;
    writeback(mem_out);
}

void writeback(int mem_out){ //writes to the register file
    if(regwr){
        reg_file[writeport] = mem2reg ? mem_out : ALUresult; //writing to the register file from memory or the ALU
    }
    clk++;
}

int main(){ //driver code

    data_mem[0]=9;
    data_mem[1]=7;
    data_mem[2]=3;
    data_mem[3]=15;
    data_mem[4]=1;
    data_mem[5]=99;
    data_mem[6]=10;
    data_mem[7]=6;
    data_mem[8]=1;
    ifstream infile("input.txt");
    ofstream outfile("output.txt");
    string line;
    while(getline(infile,line)) instr_mem.push_back(line);
    while(PC!=instr_mem.size())
    { 
        if(PC<0 || PC>= instr_mem.size())
        break;
        // cout << "PC in main = " << PC << " Value of $t0 = " << reg_file[8]<< endl;
        fetch(PC);
    }
    outfile<<"Total clock cycles = "<<clk<<"\n";
    outfile<<"Total instructions fetched = "<<clk/5<<"\n"; //This will be the case for a non-pipelined processor
    outfile<<"Nonzero registers :\n"; //prints out all nonzero registers
    for(int i=0;i<32;i++) if(reg_file[i]) outfile<<regs[i]<<" = "<<reg_file[i]<<"\n";
    outfile<<"Nonzero data memory locations :\n"; //prints out all nonzero memory locations
    for(int i=0;i<100;i++) if(data_mem[i]) outfile<<i<<" : "<<data_mem[i]<<"\n";
    outfile.close();
    infile.close();
    return 0;

}