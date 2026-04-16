---
top:
  - "[[Golang]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
related:
  - "[[Basic Golang]]"
  - "[[Atlas/Dots/Sources/Golang/Functions|Functions]]"
created: 2025-10-15
---
#### Introduction
- A way to to share memory with other parts of our program, useful for two major reasons:
	- copies large amounts of data to pass between functions -> inefficient -> passing the memory location of the data -> reduce the resource-footprint of the programs
	- passing pointers between functions -> access and modify the single copy of data directly
#### Variables and Memory
```Golang
var a int
```
- declare variable
- Go find a place in memory to store its value
- fetch value -> refer by variable name
- `a + 2` -> fetch the value stored in memory associated with `a` then adding 2 to it
- change the value -> use variable name in a assignment
#### Pointers
- sometimes useful to know the *memory address* to which the variable is pointing
- `pointers` hold the memory address of those values
- declare a pointer type -> prefixing the underlying type with an asterisk:
	```Golang
	var p *int // 'p' contains the memory address of an integer
	```
	- p will hold the memory address of an integer
	- zero value of pointers -> `nil` -> because holds no memory address
##### Getting a pointer to a variable
- find memory address of the value of variable -> use the `&` operator
- find and store the memory address of `a` in the pointer `p`:
```Golang
var a int
a = 2

var p *int
p = &a // the variable 'p' contains the memory address of 'a'
```
##### Accessing the value via a pointer (dereferencing)
- have the pointer -> want to know the value stored in the memory of pointer -> use `*` operator:
```Golang
var a int
a = 2

var p *int
p = &a // the variable 'p' contains the memory address of 'a'

var b int
b = *p // b == 2
```
- dereference operator to assign a new value to the memory address referenced by the pointer:
```Golang
var a int // declare int variable 'a'
a = 2 // assign 'a' the value of 2

var pa *int 
pa = &a // 'pa' now contains the memory address of 'a'

*pa = *pa + 2 // increment by 2 the value at memory address 'pa'

fmt.Println(a) // Output: 4
			   // 'a' will have the new value that was changed via the pointer!
```
	note: always check if pointer is not `nil` before dereferencing -> dereferencing `nil` will make the program crash at a runtime!

```Golang
var p *int // p is nil initially
fmt.Println(*p)
// panic: runtime error: invalid memory address or nil pointer dereference
```
##### Pointer to structs
- beside to primitive values, can also use pointers for structs:
```Golang
type Person struct {
	Name string
	Age int
}

var peter Person
peter = Person{Name: "Peter", Age: 22}

var p *Person
p = &peter
```
- created a new `Person` and immidiately stored a pointer to it:
```Golang
var p *Person
p = &Person{Name: "Peter", Age: 22}
```
- pointer to a struct -> don't need to dereference the pointer before accessing one of the fields:
```Golang
var p *Person
p = &Person{Name: "Peter", Age: 22}

fmt.Println(p.Name) // Output: "Peter"
					// Go automatically dereferences 'p' to allow
					// access to the 'Name' field
```
##### Slices and maps are already pointers
- slices and maps -> special type -> already a pointers
- don't need to create pointers for these type to share memory address for their values
```Golang
func incrementPeterAge(m map[string]int) { 
	m["Peter"] += 1 
}

ages := map[string]int{ "Peter": 21 } 
incrementPeterAge(ages) 
fmt.Println(ages) // Output: map[Peter:22] 
// The changes the function 'incrementPeterAge' made to the map are visible after the function ends!
```
- actions that return a new slice like `append` -> special case -> might not modify the slice outside of the function