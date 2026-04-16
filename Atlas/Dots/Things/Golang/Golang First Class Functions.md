---
top:
  - "[[Golang]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
related:
  - "[[Atlas/Dots/Sources/Golang/Functions|Functions]]"
created: 2025-08-28
---
### Functions
- First-class values
- can be used the same way as other types (integer, strings, and structs)
##### Functions as Values
- **Functions as Values**: assign functions to variables, pass them as arguments to other functions (function values -> allows for parameterize functions), return them as results from functions
	- default values -> nil
	- compares with nil to avoid panic in program
```Golang
import "fmt"

func engGreeting(name string) string {
	return fmt.Sprintf("Hello %s, nice to meet you!", name)
}

func espGreeting(name string) string {
	return fmt.Sprintf("¡Hola %s, mucho gusto!", name)
}

greeting := engGreeting // greeting is a variable of type func(string) string
fmt.Println(greeting("Alice")) // Hello Alice, nice to meet you!

greeting = espGreeting
fmt.Println(greeting("Alice")) // ¡Hola Alice, mucho gusto!
```

- not only as data but as behavior
```Golang
func dialog(name string, greetingFunc func(string) string) {
	fmt.Println(greetingFunc(name))
	fmt.Println("I'm a dialog bot.")
}

func espGreeting(name string) string {
	return fmt.Sprintf("¡Hola %s, mucho gusto!", name)
}

greeting := espGreeting
dialog("Alice", greeting)
```

##### Function Types
- **Function as Types**: custom types based on functions > make it possible for function values
	- denotes the set of all functions with the same sequence of parameter types and the same sequence of result types
	- provides flexibility
	```Golang
	type greetingFunc func(string) string
	
	func dialog(name string, f greetingFunc) {
		fmt.Println(f(name))
		fmt.Println("I'm a dialog bot.")
	}
	```
##### Functions Literarals (Closure) or Anonymous Functions
- **Functions Literals (Closures)**: anonymous functions / functions literals or closures in Go (capture and use variables from their surrounding lexical scopes), declared at the point of use, without a name, have access to the variables of the enclosing function
```Golang
func fib() func() int {
	var n1, n2 int
	
	return func() int {
		if n1 == 0 && n2 == 0 {
			n1 = 1
		} else {
			n1, n2 = n2, n1 + n2
		}
		return n2
	}
}
next := fib()
for i := 0; i < N; i++ {
	fmt.Printf("F%d\t= %4d\n", i, next())
}
```


