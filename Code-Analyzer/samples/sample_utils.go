// Package utils provides utility functions
package utils

import (
	"crypto/md5"
	"encoding/hex"
	"regexp"
	"strings"
)

// StringUtils contains string manipulation utilities
type StringUtils struct{}

// Reverse reverses a string
func (s *StringUtils) Reverse(input string) string {
	runes := []rune(input)
	for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
		runes[i], runes[j] = runes[j], runes[i]
	}
	return string(runes)
}

// IsPalindrome checks if a string is a palindrome
func (s *StringUtils) IsPalindrome(input string) bool {
	cleaned := strings.ToLower(strings.ReplaceAll(input, " ", ""))
	return cleaned == s.Reverse(cleaned)
}

// HashMD5 returns MD5 hash of a string
func HashMD5(input string) string {
	hash := md5.Sum([]byte(input))
	return hex.EncodeToString(hash[:])
}

// Validator provides validation utilities
type Validator struct {
	emailRegex *regexp.Regexp
}

// NewValidator creates a new validator
func NewValidator() *Validator {
	return &Validator{
		emailRegex: regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`),
	}
}

// ValidateEmail validates an email address
func (v *Validator) ValidateEmail(email string) bool {
	return v.emailRegex.MatchString(email)
}

// ValidateLength validates string length
func (v *Validator) ValidateLength(input string, min, max int) bool {
	length := len(input)
	return length >= min && length <= max
}

// IsNotEmpty checks if string is not empty
func IsNotEmpty(s string) bool {
	return strings.TrimSpace(s) != ""
}

// Contains checks if slice contains element
func Contains(slice []string, element string) bool {
	for _, item := range slice {
		if item == element {
			return true
		}
	}
	return false
}

// Unique returns unique elements from slice
func Unique(slice []string) []string {
	seen := make(map[string]bool)
	result := []string{}

	for _, item := range slice {
		if !seen[item] {
			seen[item] = true
			result = append(result, item)
		}
	}
	return result
}
