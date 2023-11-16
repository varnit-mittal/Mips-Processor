.data 
result: .word   1       # Initialize the result to 1

.text
.globl main
main:
    addi  $t0,$zero, 5           # Load n into $t0
    addi  $t1,$zero, 1           # Initialize $t1 to 1 (the result)
    addi  $t2,$zero, 1           # Initialize $t2 to 1 (loop counter)
    addi $a3,$zero,0

factorial_loop:
	add $t1,$t1,$a3
    beq $t2, $t0, done   # If loop counter == n, exit the loop
    add $a1,$zero,$t2
    add $a2, $zero,$t1
    add $a3,$zero,$zero
    addi $t2,$t2,1
    j multiply_loop
    
multiply_loop:
    beq $a1,$zero, factorial_loop          # If num2 == 0, exit the loop
    add $a3, $a3, $a2       # Add num1 to accumulator
    addi $a1, $a1, -1        # Decrement num2
    j multiply_loop    

done:
    sw  $t1, result      # Store the result in memory

    # Exit the program
