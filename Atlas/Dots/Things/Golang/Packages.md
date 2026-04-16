---
top:
  - "[[Golang]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
created: 2025-08-29
---

- collection of source files located in the same folder
- All source files in the folder must have the same package name at the top of the file
- named to be the same as the folder
```golang
package greeting
```
- `import` : To use packages of standard library, imported using the name
```golang
package greeting

import "fmt"
```
- imported package is addressed with the package name
```golang
world := "World" 
fmt.Sprintf("Hello %s", world)
```
- public entities (function, type, variable, constant or struct) : start with a capital letter
	- externally visible
	- can be called  by code in other packages
- private : start with non capital letter