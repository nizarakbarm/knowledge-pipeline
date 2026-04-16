---
top:
  - "[[Golang]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
created: 2025-08-30
---
	### Slices
- similar to lists or arrays > hold specific type (or interface)
- based on arrays, different in dynamically-sized, flexible elements of an array
- written like `[]T` (`T` :  the type of elements in the slice)
```golang
var empty []int // empty slice
withData := []int{0,1,2,3,4,5} // slice pre-filled with some data
```
- get an element:
```golang
withData[1] = 5
x := withData[1] // x is now 5
```
- create a new slice by getting a range of elements of existing slice:
	- specify starting (inclusive) and ending (exclusive) index using square-bracket
	- no starting index -> defaults to 0
	- no ending index -> defaults to the length of the slice
```golang
newSlice := withData[2:4]
// => []int{2,3}
newSlice := withData[:2]
// => []int{0,1}
newSlice := withData[2:]
// => []int{2,3,4,5}
newSlice := withData[:]
// => []int{0,1,2,3,4,5}
```
- add elements to slice : [`append`](https://pkg.go.dev/builtin#append) function
	- always return a new slice -> need to reassign to the slice variable
```golang
a := []int{1, 3}
a = append(a, 4, 2)
// => []int{1, 3, 4, 2}
```
