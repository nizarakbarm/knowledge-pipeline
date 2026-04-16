---
top:
  - "[[Golang]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
related:
  - "[[Basic Golang]]"
  - "[[Atlas/Dots/Sources/Golang/Functions|Functions]]"
  - "[[Atlas/Dots/Sources/Golang/Maps|Maps]]"
  - "[[Go Pointers]]"
  - "[[Booleans]]"
  - "[[Floating-point numbers]]"
  - "[[Numbers]]"
  - "[[Strings]]"
  - "[[Struct]]"
created: 2025-10-20
---
- Go -> no concept of empty, null, or undefined variable values
- no explicit initial value default to the zero value to their respective type
- zero values:
	- booleans: false
	- numeric types: 0
	- strings: ""
	- `nil` -> means zero -> for more complex types (pointers, functions, interfaces, slices, channels, maps)
	- `struct` -> depends on its fields
	