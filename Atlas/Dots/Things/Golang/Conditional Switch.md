---
top:
  - "[[Golang]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
related:
  - "[[Comparison]]"
created: 2025-08-30
---
- Switch statement as other languages
- shorter way of `if - else` statements
#### Basic Usage
- start with keyword `switch`
- followed by a value expression
- declare conditions in `case` keyword
- declare `default` case > when none of previous `case` conditions matched
```golang
operatingSystem := "windows"

switch operatingSystem {
	case "windows":
		// do something if system is windows
	case "linux":
		// do something if system is linux
	case "macos":
		// do something if system is macos
	default:
		// do something if none above is matched
}

```
- run same piece of code for several cases > group them together in single `case` by separating with `,`:
```golang
operatingSystem := "windows"

switch operatingSystem { 
	case "windows", "linux": 
		// do something if the operating system is windows or linux 
	case "macos": 
		// do something if the operating system is macos 
	default: 
		// do something if the operating system is none of the above 
}
```

#### Case with boolean expressions
- value after `switch` keyword can be omitted
- then have boolean conditions for each `case`
- to write complex `if ... else` statements
```golang
age := 21

switch {
	case age > 20 && age < 30:
		// do something if age is between 20 and 30
	case age == 10:
		// do something if age is equal to 10
	default:
		// do something else for every other case
}
```

#### Fallthrough

- condition in a `case` matches > will not evaluate the other `case`conditions
- could use `fallthrough` keyword > to evaluate the other `case` conditions
```golang
age := 21

switch {
	case age > 20:
		// do something if age is greater than 20
		fallthrough
	case age > 30:
		// Since the previous case uses 'fallthrough'
		// this code will now run if age is also greater than 30
	default:
		// do something else for every other case
}
```