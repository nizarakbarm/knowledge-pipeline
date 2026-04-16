---
top:
  - "[[Golang]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
related:
created: 2025-10-20
---
- regexp package: for regular expressions in Go
- syntax: same as general syntax used by Perl, Python, and other languages
- Search patterns & input texts -> interpreted as UTF-8
- using backticks (\`)  to make strings -> backslashes (\) no special meaning, cannot escape, and not mark the beginning of special chars (tabs \t or newlines \n)
```Golang
"\t\n" // regular string literal with 2 characters: a tab and a newline
`\t\n`// raw string literal with 4 characters: two backslashes, a 't', and an 'n'
```
- this makes backticks is desirable for regular expressions -> as no need to escape backslashes
```Golang
"\\" // string with a signle backslash
`\\` // string with 2 backslashes
```
##### Compiling Patterns - `RegExp`
- use regular expressions -> need to compile the pattern first : taking the string pattern and converting it into an internal representation (compile once and use many times)
- type `regexp.RegExp` -> a compiled regular expression
- uses `regexp.Compile`, if compilation failed returns nil and an error
```Golang
re, err := regexp.Compile(`(a|b)+`)
fmt.Println(re, err) // => (a|b)+ <nil>
re, err = regexp.Compile(`a+b)+`)
fmt.Println(re, err) // => <nil> error parsing regexp: unexpected ):`a|+b)`
```
- `MustCompile` alternative of `Compile` -> no need to handle error

> [!CAUTION] Caution
> `MustCompile` should only be used if already sure the pattern will compile, otherwise the program will panic

##### Regular Expression Methods
- 16 `Regexp` methods, the names of the methods:
```Golang
Find(All)?(String)?(Submatch?)(Index)?
```

- `All` -> matches successive non-overlapping matches of the entire expression
- `String` -> the argument is a string; otherwise slices of bytes; return values are adjusted as appropriate
- `Submatch` -> return value is a slice identifying the successive submatches of the expression
- `Index` -> matches and submatches are identified by byte index pairs within the input string

There are more than 40 functions and methods. See [regexp package - regexp - Go Packages](https://pkg.go.dev/regexp)

- `MatchString` Examples -> whether a string contains any match of regex
```Golang
re = regexp.MustCompile(`[a-z]+\d*`)
b = re.MatchString("[a12]") // => true
b = re.MatchString("12abc34(ef)") // => true
b = re.MatchString(" abc!") // => true
b = re.MatchString("123 456") // => false
```
- `FindString` Examples -> a string holding the text of the leftmost match of the regex
```Golang
re = regexp.MustCompile(`[a-z]+\d*`)
s = re.FindString("[a12]") // => "a12"
s = re.FindString("12abc34(ef)") // => "abc34"
s = re.FindString(" abc!") // => "abc"
s = re.FindString("123 456") // => ""
```
- `FindStringSubmatch` Examples -> a slice of strings holding the text of the lefmost match of regex and the matches, if any, of its subexpressions. (for capturing groups). `nil` returns value -> no match.
```Golang
re = regexp.MustCompile(`[a-z]+(\d*)`)
sl = re.FindStringSubmatch("[a12]") // => []string{"a12","12"}
sl = re.FindStringSubmatch("12abc34(ef)") // => []string{"abc34","34"}
sl = re.FindStringSubmatch(" abc!") // => []string{"abc",""}
sl = re.FindStringSubmatch("123 456") // => <nil>
```
- `ReplaceAllString` Examples -> `re.ReplaceAllString(src,repl)` -> returns a copy of `src`, replacing matches of the regex `re` with the replacement string `repl`
```Golang
re = regexp.MustCompile(`[a-z]+\d*`)
s = re.ReplaceAllString("[a12]", "X") // => "[X]"
s = re.ReplaceAllString("12abc34(ef)", "X") // => "12X(X)"
s = re.ReplaceAllString(" abc!", "X") // => " X!"
s = re.ReplaceAllString("123 456", "X") // => "123 456"
```
- `Split` Examples -> `re.Split(s,n)` -> slices a text `s` into substrings separated by the expression and returns a slice of the substrings between those expression matches. Thee count `n` -> the maximal number of substrings to return. If `n<0`, returns all substrings
```Golang
re = regexp.MustCompile(`[a-z]+\d*`)
sl = re.Split("[a12]", -1) // => []string{"[","]"}
sl = re.Split("12abc34(ef)", 2) // => []string{"12", "(ef)"}
sl = re.Split(" abc!", -1) // => []string{" ", "!"}
sl = re.Split("123 456", -1) // => []string{"123 456"}
```