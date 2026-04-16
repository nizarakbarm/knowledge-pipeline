---
top:
  - "[[Golang]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
related:
  - "[[Interfaces]]"
  - "[[Type Definitions]]"
created: 2025-10-21
---
- interface -> for defining the string format of values
- consists of a single `String` method
```Golang
type Stringer interface {
	String() string
}
```
- types need to have a `String()` method that returns a human-friendly to implement this
- `fmt` package (and many others) will look for this method to format and print values
##### Example: Distances
```Golang
type DistanceUnit int

const (
	Kilometer DistanceUnit = 0
	Mile      DistanceUnit = 1
)

type Distance struct {
	number float64
	unit DistanceUnit
}
```
- `Kilometer` and `Mile` are constants of type `DistanceUnit`
- not implement interface `Stringer` -> lack the `String` method -> `fmt` will not print `Distance` values using Go's default format:
```Golang
mileUnit := Mile
fmt.Sprint(mileUnit)
// => 1
// The result is '1' because that is the underlying value of the 'Mile' constant (see constant declarations above)

dist := Distance{number: 790.7, unit: Kilometer}
fmt.Sprint(dist)
// => {790.7 0}
// not very meaningful output!
```
- need `Stringer` for `DistanceUnit` and `Distance` types by adding string method -> to make the output more informative
```Golang
func (sc DistanceUnit) String() string {
	units := []string{"km", "mi"}
	return units[sc]
}

func (d Distance) String() string {
	return fmt.Sprintf("%v %v", d.number, d.unit)
}
```
- `fmt` package functions uses these methods when formatting `Distance` values
```Golang
kmUnit := Kilometer
kmUnit.String()
// km

mileUnit := Mile
mileUnit.String()
// mi

dist := Distance{
	number: 790.7
	unit: Kilometer,
}
dist.String()
// => 790.7 km
```