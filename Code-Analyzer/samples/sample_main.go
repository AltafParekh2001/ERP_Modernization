// Package main demonstrates a simple Go application
// This file is used for testing the Go analyzer
package main

import (
	"fmt"
	"strings"
)

// MaxRetries is the maximum number of retry attempts
const MaxRetries = 3

// DefaultTimeout is the default timeout in seconds
const DefaultTimeout = 30

// Config holds application configuration
type Config struct {
	Host    string
	Port    int
	Debug   bool
	timeout int // unexported field
}

// Server represents an HTTP server
type Server struct {
	config  *Config
	running bool
}

// NewServer creates a new server instance
func NewServer(config *Config) *Server {
	return &Server{
		config:  config,
		running: false,
	}
}

// Start starts the server
func (s *Server) Start() error {
	if s.running {
		return fmt.Errorf("server already running")
	}
	s.running = true
	fmt.Printf("Server started on %s:%d\n", s.config.Host, s.config.Port)
	return nil
}

// Stop stops the server
func (s *Server) Stop() error {
	if !s.running {
		return fmt.Errorf("server not running")
	}
	s.running = false
	return nil
}

// IsRunning returns whether the server is running
func (s *Server) IsRunning() bool {
	return s.running
}

// Greeter is an interface for greeting
type Greeter interface {
	Greet(name string) string
	Farewell(name string) string
}

// SimpleGreeter implements the Greeter interface
type SimpleGreeter struct {
	prefix string
}

// Greet returns a greeting message
func (g *SimpleGreeter) Greet(name string) string {
	return fmt.Sprintf("%s Hello, %s!", g.prefix, name)
}

// Farewell returns a farewell message
func (g *SimpleGreeter) Farewell(name string) string {
	return fmt.Sprintf("Goodbye, %s!", name)
}

// processData processes input data
func processData(data string) string {
	data = strings.TrimSpace(data)
	data = strings.ToUpper(data)
	return data
}

// calculateSum calculates sum of numbers
func calculateSum(numbers []int) int {
	sum := 0
	for _, num := range numbers {
		sum += num
	}
	return sum
}

// findMax finds the maximum value in a slice
func findMax(numbers []int) (int, error) {
	if len(numbers) == 0 {
		return 0, fmt.Errorf("empty slice")
	}

	max := numbers[0]
	for _, num := range numbers {
		if num > max {
			max = num
		}
	}
	return max, nil
}

func main() {
	config := &Config{
		Host:  "localhost",
		Port:  8080,
		Debug: true,
	}

	server := NewServer(config)
	if err := server.Start(); err != nil {
		fmt.Println("Failed to start:", err)
		return
	}

	greeter := &SimpleGreeter{prefix: ">>"}
	fmt.Println(greeter.Greet("World"))

	numbers := []int{1, 2, 3, 4, 5}
	fmt.Println("Sum:", calculateSum(numbers))

	if max, err := findMax(numbers); err == nil {
		fmt.Println("Max:", max)
	}
}
