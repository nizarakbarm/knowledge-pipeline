---
top:
  - "[[Golang]]"
in:
  - "[[Concepts]]"
  - "[[Things]]"
related:
  - "[[Basic Golang]]"
  - "[[Atlas/Dots/Sources/Golang/Maps|Maps]]"
  - "[[Slices]]"
  - "[[For Loop]]"
created: 2025-10-15
---
- iterate over `slice` using `for` and an index
- use `range` -> also allows iterate over a `map`
- Iterate over a slice -> ordered as expected
```Golang
xi := []int{10, 20, 30}
for i, x := range xi {
	fmt.Println(i, x)
}
// outputs:
// 0, 10
// 1, 20
// 3, 30
```
- Iterate over a map -> the order is random
```Golang
hash := map[int]int{9: 10, 99: 20, 999: 30}
for k, v := range hash {
	fmt.Println(k, v)
}
// outputs, for example
// 99 20
// 999 30
// 9 10
```
	 ( the result became like this because maps are unordered by nature)
 - iteration omitting key or value
	 - unused value -> raise an error at build time -> sometime only need value:
	```Golang
	xi := []int{10, 20, 30}
	for i, x := range xi {
		fmt.Println(x)
	}
	// Go build failed: i declared but not used
	```
	 - can replace the `i` with `_` -> tell compiler don't use that value:

```Golang
xi := []int{10, 20, 30}
for _, x := range xi {
	fmt.Println(x)
}
// outputs:
// 10
// 20
// 30
```

