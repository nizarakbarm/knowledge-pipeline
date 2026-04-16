---
top:
  - "[[Golang]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
created: 2025-08-29
---

Go contains basic numbering types:
- `int` : a signed integer at least 32 bits (value range of: -2147483648 through 2147483647), some modern architecture use 64 bits -> `int` will be 64 bits (value rate of: -9223372036854775808 through 9223372036854775807)
- `float64`: a set of all 64-bit floating-point numbers
- `uint`: an unsigned integer, same size as `int`(value range of: 0 through 4294967295 for 32 bits and 0 through 18446744073709551615 for 64 bits)
conversion is done using Type Conversion

- didn't support arithmetic number operations in different type between operand

### Converting Between Types
- via function with the name of type to convert to
