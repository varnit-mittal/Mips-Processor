.data

.text

	lw $t1, 0($zero)
	lw $t2, 4($zero)
	add $t3, $t2, $t1
	sw $t3, 12($zero)
	lw $t4, 8($zero)
	add $t5, $t1, $t4
	sw $t5, 16($zero)