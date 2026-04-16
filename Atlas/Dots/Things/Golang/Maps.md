---
top:
  - "[[Golang]]"
in:
  - "[[Concepts]]"
  - "[[Things]]"
related:
  - "[[ints]]"
  - "[[Atlas/Dots/Sources/Golang/Functions|Functions]]"
created: 2025-10-15
---
- built-in data type -> maps keys to values
- at other programming languages is dictionary, hash table, key/value store or an associative array
- syntatically, look like this:
  ```Golang
  map[KeyType]ElementType
  ```
  - each key is unique
  - to create map:
  ```Golang
  // With map literal
  foo := map[string]int{}
  ```
  or
```Golang
// or with make function
foo := make(map[string]int)
```
some operations can do with map:
```Golang
// Add a value in map with line `=` operator
foo["bar"] = 42
// Here we update the element of `bar`
foo["bar"] = 73
// To retrieve a map value, you can use
baz := foo["bar"]
// To delete an item from a map, you can use
delete(foo, "bar")
```
- retrieve the value for nonexistent key in the map -> return zero value of the value type -> can confuse if the default value is a valid value -> to check if a key exists, can use:
```Golang
value, exists := foo["baz"]
// If the key "baz" does not exists,
// value: 0; exists: false
```