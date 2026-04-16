---
top:
  - "[[Golang]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
created: 2025-08-29
---

Language Behaviour:
- statically typed
- compiled

Go are organized into packages
Packages is a collection of:
- source file located in the same directory
- share same package name

When packages imported only public entities can be used or accessed:
- start with capital letter

Variables:
- statically typed -> have defined type at compile-time
- can be defined 
	- by explicitly defining the type
	```golang
	var explicit int // statically typed as integer
	```
	- use initializer
	```golang
		implicit := 10 // implicitly typed as integer
	```
- once declared can be assigned value with =
Constants:
- like variables
- but value cannot change
- defined using `const` keyword
	- numbers, characters, or booleans
