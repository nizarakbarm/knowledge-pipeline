---
top:
  - "[[Golang]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
related:
  - "[[Slices]]"
created: 2025-08-30
---

- a function > accepts a variable number of arguments
- last parameter of function is `...` : the function can accept any number of arguments for that parameter
	- must be the last parameter
- works by converting the variable number of arguments to a slice of the type of the variadic parameters

```golang
func find(a int, b ...int) {
	// ...
}
```
example the usage of function:
```golang
find(5, 6) 
find(5, 6, 7) 
find(5)
```

example:
```golang
func find(num int, nums ...int) { 
	fmt.Printf("type of nums is %T\n", nums) 
	for i, v := range nums { 
		if v == num { 
			fmt.Println(num, "found at index", i, "in", nums) 
			return 
		} 
	} 
	fmt.Println(num, "not found in ", nums) 
} 

func main() { 
	find(89, 90, 91, 95) 
	// => 
	// type of nums is []int 
	// 89 not found in [90 91 95] 
	find(45, 56, 67, 45, 90, 109) 
	// => 
	// type of nums is []int 
	// 45 found at index 2 in [56 67 45 90 109] 
	find(87) 
	// => 
	// type of nums is []int 
	// 87 not found in [] 
}
```
