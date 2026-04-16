---
top:
  - "[[Golang]]"
in:
  - "[[Things]]"
  - "[[Concepts]]"
related:
  - "[[Numbers]]"
  - "[[Slices]]"
created: 2025-09-06
---
### Intro
- generating pseudo-random numbers supported by package `mat/rand`
- Generating random integer (see [rand.Intn](https://pkg.go.dev/math/rand#Intn))
```Golang
n := rand.Intn(100) // n is a random int, 0 <= n < 100
```
- [rand.Float64](https://pkg.go.dev/math/rand#Float64)  for a random floating point number between 0.0 and 1.0:
```Golang
f := rand.Float64() // f is a random float64, 0.0 <= f < 1.0
```
- shuffling a slice (or other data structure):
```Golang
x := []string{"a", "b", "c", "d", "e"}
// shuffling the slice put its element into a random order
rand.Shuffle(len(x), func(i, j int) {
	x[i], x[j] = x[j], x[i]
})
```
### Seeds
- `math/rand` are not generating truly random
- By specific "seed" value > deterministic
- Seed is picked at random > different sequences of random  (in Go 1.20+)
- Prior Go 1.20+, seed was 1 by default > need to manually seed random number generator before retrieving any random numbers
```Golang
rand.Seed(time.Now().UnixNano())
```
