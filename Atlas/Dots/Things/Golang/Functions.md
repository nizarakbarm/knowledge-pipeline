---
top:
  - "[[Golang]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
related:
  - "[[Slices]]"
created: 2025-09-06
---
### Intro
- Group code into a reusable unit
- use `func` keyword, the name of function, and zero or more parameters (comma separated) and types in round brackets
### Function Parameters
- explicitly typed (required)
- no type inference for parameters
- no default values (are functions parameters are required if defined) (not like Python)
```Golang
import "fmt"

// No parameters
func PrintHello() {
	fmt.Prrintln("Hello")
}


// Two parameters
func PrintGreetingName(greeting string, name string) {
	fmt.Println(greeting + " " + name)
}
```
- same type parameters can be declared together with single type declaration
```Golang
import "fmt"

func PrintGreetingName(greeting, name string) {
	fmt.Println(greeting + " " + name)
}
```

### Parameters vs Arguments
- Function **parameters** > defined in the function's signature, e.g. `greeting` and `name` in function `PrintGreetingName`
- Function **arguments** > concrete values passed to the function parameters when it's invoked
```Golang
PrintGreetingName("Hello", "Katrina") // "Hello" and "Katrina" are function arguments
```

### Return Values
- zero or more return values (must be explicitly typed)
- single return values are left bare
- multiple return values are wrapped in parenthesis
- can me multiple `return` statements
- multiple values are returned > comma separated
```Golang
func Hello(name string) string {
	return "Hello " + name
}

func HelloAndGoodbye(name string) (string, string) {
	return "Hello " + name, "Goodbye " + name
}
```

### Invoking Functions
- specifying function name and passing arguments 
```Golang
import "fmt"

// No parameters, no return value
func PrintHello() {
	fmt.Println("Hello")
}
// Called like this
PrintHello()

// One parameter, one return value
func Hello(name string) string {
	return "Hello " + name
}

// Called like this:
greeting := Hello("Dave")

// Multiple parameters, multiple return values
func SumAndMultiply(a, b int) (int, int) {
	return a+b, a*b
}

// Called like this:
aplusb, atimesb := SumAndMultiply(a, b)

```

### Named Return Values and Naked Return
- return values can optionally be named > a `return` statement without arguments will return the values of the named variable in return definition (named return)
```Golang
func SumAndMultiplyThenMinus(a, b, c int) (sum, mult int) {
	sum, mult = a+b, a*b
	sum -= c
	mult -= c
	return
}
```

### Pass by Value vs Pass by Reference
- pass by value : pass variable but only a copy of the variable passed in the function, the original value of variable still remains
```Golang
val := 2
func MultiplyByTwo(v int) int {
	v = v * 2
	return v
}
newVal := MultiplyByTwo(val)
// newVal is 4, val is still 2 becaus only a copy its value was passed into the function
```
- pass by reference: use **pointers** as arguments

### Pointers
- to achive passing by reference
- passing **pointer** arg to a function: data passed to the function could be modified
- can be recognized by the **`*`** in front of the  type
```Golang
func HandlePointers(x, y *int) {
	// Some logic to handle integer values referenced by pointers x and y
}
```

### Maps and Slices in Argument
- treated as pointer types without explicit `*` in the type > could modify its underlying data
