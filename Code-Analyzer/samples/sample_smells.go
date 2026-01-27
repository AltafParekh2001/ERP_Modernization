// Package smells contains intentional code smells for testing detection
package smells

import "fmt"

// This file intentionally contains code smells for testing

// badFunction has too many parameters (code smell)
func badFunction(a int, b int, c int, d int, e int, f int, g int) int {
	return a + b + c + d + e + f + g
}

// magicNumbers uses magic numbers (code smell)
func magicNumbers(value int) int {
	if value > 42 {
		return value * 7
	}
	return value + 13
}

// emptyErrorHandling ignores errors (code smell)
func emptyErrorHandling() {
	_, err := fmt.Println("test")
	if err != nil {
		// Empty error handling - BAD!
	}
}

// ignoredError uses blank identifier for error (code smell)
func ignoredError() {
	_, _ = fmt.Println("ignoring error")
}

// nakedReturn uses naked returns (code smell)
func nakedReturn(x int) (result int) {
	result = x * 2
	return // naked return
}

// longFunction is too long (code smell)
func longFunction(input string) string {
	// Line 1
	result := input
	// Line 2
	result = result + "a"
	// Line 3
	result = result + "b"
	// Line 4
	result = result + "c"
	// Line 5
	result = result + "d"
	// Line 6
	result = result + "e"
	// Line 7
	result = result + "f"
	// Line 8
	result = result + "g"
	// Line 9
	result = result + "h"
	// Line 10
	result = result + "i"
	// Line 11
	result = result + "j"
	// Line 12
	result = result + "k"
	// Line 13
	result = result + "l"
	// Line 14
	result = result + "m"
	// Line 15
	result = result + "n"
	// Line 16
	result = result + "o"
	// Line 17
	result = result + "p"
	// Line 18
	result = result + "q"
	// Line 19
	result = result + "r"
	// Line 20
	result = result + "s"
	// Line 21
	result = result + "t"
	// Line 22
	result = result + "u"
	// Line 23
	result = result + "v"
	// Line 24
	result = result + "w"
	// Line 25
	result = result + "x"
	// Line 26
	result = result + "y"
	// Line 27
	result = result + "z"
	// Line 28
	return result
}

// UndocumentedExported is exported but has no doc comment (code smell)
func UndocumentedExported() {
	// Missing documentation
}

// panicInLibrary panics instead of returning error (code smell for library code)
func panicInLibrary() {
	panic("this is bad in library code")
}

// init function (potentially problematic)
func init() {
	fmt.Println("init called")
}

// deeply nested code (code smell)
func deeplyNested(x int) int {
	if x > 0 {
		if x > 10 {
			if x > 100 {
				if x > 1000 {
					return x
				}
			}
		}
	}
	return 0
}
