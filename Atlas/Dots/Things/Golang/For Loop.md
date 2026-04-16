---
top:
  - "[[Golang]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
related:
  - "[[Numbers]]"
created: 2025-09-03
---
### General Syntax
- most commonly used statements to repeatedly execute some logic
- In Go, consists:
	- header, consits of (separated by semicolon `;`):
		- **init**: initial code ran at the beginning of the loop
		- **condition**: expression that evaluates to a boolea, controls when the loop should stop, run when condition is true and stop when the condition is false
		- **post**: post code ran at the end of each iteration
	- a code : block that contains the body of the loop (inside curly brackets)
	- no parentheses `()` as other language, the braces `{}` is required
### Example
- init: set up a counter variable
- condition: checks to continue or stop based on the condition
- post: increments the counter at the end of each repetition
```Golang
for i := 1; 1 < 10; i++ {
	fmt.Println(i)
}
```
### Optional components of the header
- **init** and **post** are optional > will create a while loop in Go as there is no `while` keyword
```Golang
var sum = 1
for sum < 1000 {
	sum += sum
}
fmt.Println(sum)
// Output: 1024
```
### Break and Continue
- `break` : stop the execution of the loop entirely
```Golang
for n := 0; n <= 5; n++ {
	if n == 3 {
		break
	}
	fmt.Println(n)
}
// Output:
// 0
// 1
// 2
```
- `continue` : stop the execution of the current iteration and continues to the next one
```Golang
for n := 0; n <= 5; n++ {
	if n%2 == 0 {
		continue
	}
	fmt.Println(n)
}
// Output:
// 1
// 3
// 5
```
### Infinite for loop
- conditional part also optional > creates infinite for loop : loop endlessly, will finish if the program exit or has a `break`
```Golang
for {
	// Endless loop...
}
```
### Labels and goto
- can set a label
- `break` to the location of the label
- `continue` to the location of the label
```Golang
OuterLoop:
	for i := 0; i < 10; i++ {
		for j := 0; j < 10; j++ {
			// ...
			break OuterLoop
		}
	}
```
- also has `goto` keyword : works in a similar way, allows to jump to from a pice of code to another labeled piece of code
> [!warning] jump with label, can easily make the code very hard to read, so labels is often not recommended
