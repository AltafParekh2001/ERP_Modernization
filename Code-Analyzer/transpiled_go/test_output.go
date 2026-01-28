package main


import (
	"fmt"
)

func Calculate_sum(numbers interface{}) int {
		total := 0
		for _, num := range numbers {
			total += num
		}
		return total
}

func Find_max(items interface{}) int {
		if !items {
			return 0
		}
		max_val := items[0]
		for _, item := range items {
			if item > max_val {
				max_val = item
			}
		}
		return max_val
}
