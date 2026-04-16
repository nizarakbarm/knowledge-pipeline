---
top:
  - "[[Python]]"
related:
  - "[[ints]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
created: 2025-09-06
---
three different kinds of built-in numbers:
- [[ints]]
- [[floats]]
- [[complex]]

Support Arithmetic operations between `ints` and `floats`
- convert narrower numbers to match their less narrow counterparts in
	- `+`
	- `-`
	- `*`
	- `/` -> always return float
	- `//` (return quotient) -> should be used if need int result
	- `%` (return remainder)
- ints narrower than float
- convert between type using `[type_name]()`

