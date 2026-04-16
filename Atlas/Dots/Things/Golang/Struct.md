---
top:
  - "[[Golang]]"
in:
  - "[[Concepts]]"
  - "[[Things]]"
related:
created: 2025-09-03
---
### What is struct in Go?
- a sequence of named elements called *fields*, which each has
	- name: unique within the struct
	- type

### Defining a struct
- by using the `type` and `struct` keywords, and explicitly define
	- name of the fields, and
	- type of the fields
	
	```Golang
	type Shape struct {
		name string
		size int
	}
	```
	- names follow Go convention:
		- starts with lower case letter: only visible to code in the same package (private)
		- starts with upper case letter: visible in other packages (public)
### Creating instances of a struct
- defining the fields using their field name in any order
	```Golang
	s := Shape {
		name: "Square",
		size: 25,
	}
	```
- read or modify instance fields:
```Golang
// Update the name and the size
s.name = "Circle"
s.size = 35
fmt.Printf("name: %s size: %d\n", s.name, s.size)
// Output: name: Circle size: 35
```
- fields don't have an initial value -> will have their zero value:
```Golang
s := Shape{name: "Circle"}
fmt.Printf("name: %s size: %d\n", s.name, s.size)
// Output: name: Circle size: 0
```
- create an instance of a `struct` without field names -> define the fields in order
	- a brittle code -> can break when a field is added especially when the new field has different type

```Golang
s := Shape{
	"Oval",
	20,
}
```

- example of defining without fields have brittle code:
```Golang
type Shape struct {
	name string
	description string // new field "description" added > could cause brittle code when defined
	size int
}

s := Shape {
	"Circle",
	20, // should be string, but got int > error when compiling
}
// Output: cannot use 20 (type untyped int) as type string in field value 
// Output: too few values in Shape{...}
```

### "New" functions
- `New` : functions that helps create struct instances
- regular functions: can give any name > similar with constructor in other programming language but in Go just regular functions
- example `New` to create new instance of `Shape`, automatically set a default value for the `size`:
```Golang
func NewShape(name string) shape {
	return Shape{
		name: name,
		size: 100, // default-value for size is 100
	}
}

NewShape("Triangle")
// => Shape { name: "Triangle", size: 100}
```
- advantages of `New` functions:
	- validation of the given values
	- handling of default-values
	- can initialize even private fields of the struct as declared in the same package of the structs
### `new` builtin
```Golang
s := new(Shape) // s will be of type *Shape (pointer to shape)
fmt.Printf("name: %s size: %d\n", s.name, s.size)
// Output: name: size: 0
```
- creates an instance of the struct `Shape` > all value initialized to the zero value of their type > returns a pointer to it
- note: should be used as last resort