---
top:
  - "[[Golang]]"
in:
  - "[[Concepts]]"
  - "[[Things]]"
related:
  - "[[Basic Golang]]"
  - "[[Strings]]"
  - "[[Slices]]"
  - "[[Atlas/Dots/Sources/Golang/Maps|Maps]]"
created: 2025-10-15
---
#### Non-struct types
- non struct types (beside struct) as an alias for a built-in type declaration
- could be used for receiver functions to extend them
```Golang
type Name string
func SayHello(n Name) {
	fmt.Printf("Hello %s\n", n)
}
n := Name("Fred")
SayHello(n)
// Output: Hello Fred
```
- define non-struct types composed of arrays and maps
```Golang
type Names []string
func SayHello(n Names) {
	for _, name := range n {
		fmt.Printf("Hello %s\n", name)
	}
}
n := Names([]string{"Fred", "Bill"})
SayHello(n)
// Output:
// Hello Fred
// Hello Bill
```