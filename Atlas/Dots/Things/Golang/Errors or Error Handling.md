---
top:
  - "[[Golang]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
related:
  - "[[Atlas/Dots/Sources/Golang/Functions|Functions]]"
  - "[[Methods]]"
created: 2025-10-21
---
- not done via exceptions in Go
- errors -> normal values of type in the built-in `error` interface
- `error` interface -> very minimal -> contains only one method `Error()` returns the error message as a string
```Golang
type error interface {
	Error() string
}
```
- Every time defining function with an possibility error could happen -> need to include `error` as one of the return types -> multiple return values -> `error ` is the last return value (by convention)
```Golang
func DoSomething() (int, error) {
	// ...
}
```
##### Creating and returning a simple error
- could create simple error without interface -> use `errors.New()` (part of the standard library package `errors`)
- pass the error message as string in the argument -> `errors.New()` will create a value with the message and implements `error` interface
- good practice -> return the zero value for all other parameters if returns error
```Golang
func DoSomething() (SomeStruct, int, error) {
	// ...
	return SomeStruct{}, 0, errors.New("failed to calculate result")
}
```

> [!CAUTION] Caution
> - should not assume that all functions return zero values for other return values if error
> - best practice: assume not safe to use any of the other return values if error occurred
> - exceptions: case with docs clearly states that other return values are meaningful in case of an error
- want to use simple error in multiple places -> should declare variable for the error instead `errors.New` in-line -> name of variable should start `Err` or `err` (exported or not) -> called *sentinel errors*
```Golang
import "errors"

var ErrNotFound = errors.New("resource was not found")

func DoSomething() error {
	// ...
	return ErrNotFound
}
```
- no errors during function execution -> returns `nil` on the error returns part
```Golang
func Foo() (int, error) {
	return 10, nil
}
```
##### Error Checking
- call a function that returns an error -> store error value in variable `err`
- should check that there was no error and error should be handled first
- use != or == to handle error (compare against `nil`) -> no error means  not `nil`
```Golang
func processUserFile() error {
	file, err := os.Open("./users.csv")
	if err != nil {
		return err
	}
	
	// do something with the file
}
```
- beside returning the error in case error in function -> could log it and continue with another operation (only choose one returning or logging)
##### Custom Error Types
- custom error type -> an error that include more information than just the error message string -> created with struct -> convention name should end with `Error`
- everything that implement `error` interface (use `Error() string` method) -> serve as an error in Go
- Best : set up the `Error() string` method with a pointer receiver
- need to return a pointer to the custom error, otherwise will not count as `error` 
```Golang
type MyCustomError struct {
	message string
	details string
}

func (e *MyCustomError) Error() string {
	return fmt.Sprintf("%s, details: %s", e.message, e.details)
}

func someFunction() error {
	// ...
	return &MyCustomError{
		message: "...",
		details: "...",
	}
}
```