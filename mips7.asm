.data

.text
	addi $t1,$zero,0
	addi $t2,$zero,8
	addi $s4,$zero,1

for:	
	beq $t1,$t2,done
	sub $t4,$t2,$t1
	addi $t1,$t1,1
	addi $t3,$zero,0
	j for2

for2:
	beq $t3,$t4,for
	lw $s1,0($t3)
	addi $t3, $t3,1
	lw $s2, 0($t3)
	slt $t0, $s1, $s2
	beq $t0,$s4,for2
	sw $s1,0($t3)
	sw $s2,-1($t3)
	j for2
	
done:
	addi $t4,$zero,0
