---
top:
  - "[[Golang]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
created: 2025-08-29
---

Two ways of Comment:
- `//` : single line
- `/* ... */` : multiline

Plays important role in documenting:
- used by `godoc` command
	- extracts these comments -> create documentation about Go packages
	- doc comment: complete sentence that starts with the name of the thing described and ends with a period
	- should precede packages, exported identifiers (exported functions, methods, packages variables, constants, and structs)