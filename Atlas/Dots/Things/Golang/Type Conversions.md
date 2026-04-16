---
top:
  - "[[Golang]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
related:
  - "[[Type Definitions]]"
  - "[[Interfaces]]"
  - "[[Numbers]]"
  - "[[Strings]]"
created: 2025-10-20
---
- requires explicit conversion to different types
- **type casting** -> via a function with the type name to convert to
```Golang
var x int = 42 // x has type int
f := float64(x) // f has type float64 (ie. 42.0)
```
##### Converting between primitive types and strings
- `strconv` package -> converting between primitive types (like `int`) and `string`
```Golang
import "strconv"

var intString string = "42"
var i, err = strconv.Atoi(intString)

var number int = 12
var s string = strconv.Itoa(number)
```
##### Type Assertions
- interfaces in Go -> add ambiguity about the underlying type
- type assertion -> extract the interface value's concrete underlying type -> `interfaceVariable.(concreteType)`
```Golang
var input interface{} = 12
number := input.(int)
```

> [!NOTE] Note
> will cause panic if does not hold a value of concrete type


- To test if interface holds specific concrete type:
```Golang
str, ok := input.(string) // no panic if input is string
						  // ok -> returns boolean true
						  // str will contains the string value
						  // panic if input is not string
						  // ok -> returns boolean false
						  // str will contains zero value of string ""
```

##### Type Switches
- perform several type assertion with switch
- same syntax as type assertion (`interfaceVariable.(concreteType))` -> `concreteType` replaced with keyword `type`
```Golang
var i interface{} = 12 // try 12.3, true, []int{}, map[string]int{}

switch v:= i.(type) {
	case int:
		fmt.Printf("the integer %d\n", v)
	case string:
		fmt.Printf("the string %s\n", v)
	default:
		fmt.Printf("type, %T, not handled explicitly: %#v", v, v)
}
```
