---
top:
  - "[[Golang]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
related:
  - "[[Methods]]"
  - "[[Type Definitions]]"
created: 2025-10-20
---
- simplest form -> a set of method signatures
- examples of interface definition of two methods `Add` and `Value`:
```Golang
type Counter interface {
	Add(increment int)
	Value() int
}
```
- param name like `increment` can be omitted -> but included to increase readability
- does not contain the word `Interface` or `I` -> often end with `er`, e.g. `Reader`, `Stringer`.
##### Implementing an interface
- any types defines the methods of interface -> implicitly "implements" the interface
- no `implements` keyword in Go
```Golang
type Stats struct {
	value int
	// ...
}

func (s Stats) Add(v int) {
	s.value += v
}

func (s Stats) Value() int {
	return s.value
}

func (s Stats) SomeOtherMethod() {
	// The type can have additional methods not mentioned in the interface
}
```
- does not matter whether the method has a value or pointer receiver
		A value of interface type can hold any value that implements those methods
- means `Stats` can be used in all the places that expect the `Counter` interface (as defined above)
```Golang
func SetUpAnalytics(counter Counter) {
	// ...
}

stats := Stats{}
SetUpAnalytics(stats)
// works because Stats implements Counter
```
- interface -> implemented implicitly -> a type can easily implement multiple interfaces -> only needs to have all necessary methods defined
##### Empty interface
- contains zero methods
- written like: `interface{}` in Go 1.18 or higer, `any` can be used as well
- defined as an alias
- zero methods -> every type implements it implicitly
- for defining function -> generally accept any value -> the function parameter uses the empty interface type