---
top:
  - "[[Golang]]"
in:
  - "[[Concepts]]"
  - "[[Things]]"
related:
  - "[[Strings]]"
  - "[[Slices]]"
created: 2025-10-16
---
- alias for `int32`
- holds a signed 32-bits integer value
- unlike an `int32` type, this represents a single Unicode character
##### Unicode and Unicode Code Points
- Unicode
	- superset of ASCII
	- represents characters -> by assigning a unique number to every character -> the uniq number called unicode code point
	- aims to represent all the world's characters (alphabets, numbers, symbols, and even emoji as a unicode code points)
- Go -> represents a single unicode code point -> as rune type
- Unicode characters along with their unicode code point and decimal values:

| Unicode Character | Unicode Code Point | Decimal Value |
| ----------------- | ------------------ | ------------- |
| 0                 | U+0030             | 48            |
| A                 | U+0041             | 65            |
| a                 | U+0061             | 97            |
| ¿                 | U+00BF             | 191           |
| π                 | U+03C0             | 960           |
| 🧠                | U+1F9E0            | 129504        |
##### UTF-8
- variable-width character encoding -> to encode every unicode code point as 1, 2, 3, or 4 bytes
- since unicode code point -> maximum encoded of 4 bytes -> `rune` type needs to be able to hold up to 4 bytes of data -> the reason of an alias for `int32` -> capable of holding up to 4 bytes of data
- go source code file -> encoded using UTF-8
##### Using Runes
- declared by placing a character inside a single quotes:
```Golang
myRune := '¿'
```
- just an alias for `int32` -> printing rune's type will yield `int32`:
```Golang
myRune := '¿'
fmt.Printf("myRune type: %T\n", myRune)
// Output: myRune type: int32
```
- printing rune's value -> yield integer (decimal) value:
```Golang
myRune := '¿'
fmt.Printf("myRune value: %v\n", myRune)
// Output: myRune value: 191
```
- to print the Unicode character represented by the rune -> use the `%c` formatting verb:
```Golang
myRune := '¿'
fmt.Printf("myRune unicode character: %c\n", myRune)
// Output: myRune Unicode character: ¿
```
- to print the Unicode code point represented by the run -> use the `%U` formatting verb:
```Golang
myRune := '¿'
fmt.Printf("myRune unicode code point: %U\n", myRune)
// Output: myRune Unicode code point: U+00BF
```
##### Runes and Stringss
- Strings -> encoded using UTF-8 > contains Unicode characters

- Characters in strings -> stored and encoded as 1, 2, 3, or 4 bytes  -> depends on the unicode character represented
- slices -> represent sequences -> can be iterated using range
- iterate over a string -> converts the string into a series of Runes -> each of which is 4 bytes
	- strings: slice of bytes -> but `range` iterates over a string's runes, not its bytes
- example:
	- index: starting index of current rune's byte
	- char: represents the current rune
```Golang
myString := "❗hello"
for index, char := range myString {
	fmt.Printf("Index: %d\tCharacter: %c\t\tCode Point: %U\n", index, char, char)
}
// Output:
// Index: 0	Character: ❗		Code Point: U+2757
// Index: 3	Character: h		Code Point: U+0068
// Index: 4	Character: e		Code Point: U+0065
// Index: 5	Character: l		Code Point: U+006C
// Index: 6	Character: l		Code Point: U+006C
// Index: 7	Character: o		Code Point: U+006F
```
- can be stored as 1, 2, 3, or 4 bytes -> length of a string not always equal the number of chars in the string
	- use `len` to get the length in bytes
	- `utf8.RuneCountInString` to get the number of runes in a string
```Golang
import "unicode/utf8"

myString := "❗hello"
stringLength := len(myString)
numberOfRunes := utf8.RuneCountInString(myString)

fmt.Printf("myString - Length: %d - Runes: %d\n", stringLength, numberOfRunes)
// Output: myString - Length: 8 - Runes: 6
```