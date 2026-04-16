---
top:
  - "[[Golang]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
created: 2025-08-29
---

using relational and equality operators:

| Comparison       | Operator |
| ---------------- | -------- |
| equal            | ==       |
| not equal        | !=.      |
| less             | <        |
| less or equal    | <=       |
| greater          | >        |
| greater or equal | >=       |
result > boolean (`true` or `false`)
```goolang
a := 3 
a != 4 // true 
a > 5 // false
```
can also be used to compare strings > a lexicographical (dictionary) order is applied
```golang
"apple" < "banana" // true 
"apple" > "banana" // false
```

### If statement
- underlying type : `bool` type
- often used as flow control to check various conditions
- checking particular case, execute only if conditions `true`
- can be chained `if`, `else if`, `else`
```golang
var number int
result := "This number is " 
if number > 0 {
	result += "positive" 
 } 
 else if number < 0 { 
	 result += "negative" 
 } else { 
	 result += "zero" 
 }
```
- can include a short initialization statement to initialize one or more variables
```golang
num := 7 
if v := 2 * num; v > 10 { 
	fmt.Println(v) 
} else { 
	fmt.Println(num) 
} 
// Output: 14
```