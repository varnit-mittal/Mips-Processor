.data

.text
	addi $at,$zero,6
	addi $v1,$zero,3
	addi $a1,$zero,1
	addi $a2,$zero,8
	
	add $v0,$at, $v1
	add $t4,$v0,$a1
	add $t3,$a2,$v0