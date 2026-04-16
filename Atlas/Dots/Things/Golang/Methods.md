---
top:
  - "[[Golang]]"
in:
  - "[[Concepts]]"
  - "[[Things]]"
related:
  - "[[Atlas/Dots/Sources/Golang/Functions|Functions]]"
  - "[[Basic Golang]]"
  - "[[Go Pointers]]"
created: 2025-10-16
---
- a function with special *receiver* argument -> appears between func keyword and the name of the method
```Golang
func (receiver type) MethodName(parameters) (returnTypes) {
}
```
- receiver types should be defined in the same package as the method
```Golang
package person

type Person struct {
	Name string
}

func (p Person) Greetings() string {
	return fmt.Sprintf("Welcome %s!", p.Name)
}
```
- method on the struct can be called with dot notation
```Golang
p := Person{Name: "Bronson"}
fmt.Println(p.Greetings())
// Output: Welcome Bronson!
```
- the way it's called is the same as in OOP
- a method is just a function with a receiver argument -> avoid naming conflicts -> tied to a particular receiver type -> can have same method on different types
```Golang
import "math"

type rect struct {
	width, height int
}
func (r rect) area() int {
	return r.width * r.height
}

type circle struct {
	radius int
}
func (c circle) area() float64 {
	return math.Pow(float64(c.radius), 2) * math.Pi
}
```
##### Type of Receivers
- Value Receivers
	- receive a copy of the value passed to the method -> any modification done to the receiver inside the method is not visible to the caller
- Pointer Receivers
	- modify the value which the receiver points -> by prefixing the type name with a `*`
	```Golang
	type rect struct {
		width, height int
	}
	func (r *rect) squareIt() {
		r.height = r.width
	}
	
	r := rect{width: 10, height: 20}
	fmt.Printf("Width: %d, Height: %d\n", r.width, r.height)
	// Output: Width: 10, Height: 20
	
	r.squareIt()
	fmt.Printf("Width: %d, Height: %d\n", r.width, r.height)
	// Output: Width: 10: Height: 10
	```
	