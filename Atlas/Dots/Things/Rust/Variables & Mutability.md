---
top:
  - "[[Rust]]"
---
### Mutability
- **Variables** : immutable by default -> offer advantage in safety -> has option to make mutable (by `mut` term)
```rust
fn main() {
	let x = 5;
	println!("The value of x is: {x}");
	x = 6;
	println!("The value of x is: {x}");
}
```
save then run `cargo run`
```rust
$ cargo run
   Compiling variables v0.1.0 (file:///projects/variables)
error[E0384]: cannot assign twice to immutable variable `x`
 --> src/main.rs:4:5
  |
2 |     let x = 5;
  |         - first assignment to `x`
3 |     println!("The value of x is: {x}");
4 |     x = 6;
  |     ^^^^^ cannot assign twice to immutable variable
  |
help: consider making this binding mutable
  |
2 |     let mut x = 5;
  |         +++

For more information about this error, try `rustc --explain E0384`.
error: could not compile `variables` (bin "variables") due to 1 previous error

```
- using `mut` in front of the variable name to change behavior to mutable:
```rust
fn main() {
	let mut x = 5;
	println!("The value of x is: {x}");
	x = 6;
	println!("The value of x is: {x}");
}
```
- allowed to  change the value bound to `x` from `5` to `6` when `mut` is used
### Declaring Constants
- bound to name and not allowed to change
- not allowed to use `mut`
- always immutable
- declare using `const`, type fo the value *must* be annotated
- can declared in any scope
- naming convention: uppercase with underscore between words (substitutes of space)
```rust
const THREE_HOURS_IN_SECONDS: u32 = 60 * 60 * 3;
```
### Shadowing
- redeclare the old variable name with `let` again, first variable shadowed by second variable, use variable name until shadowed again or scope end
```rust
fn main() {
	let x = 5;
	let x = x + 1;
	{
		let x = x * 2;
		println!("The value of x is: {x}");
	}
	println!("The value of x is: {x}")
}
```
- different with `mut`, reassigning create new var with same name, but if reassign without let will get compile time error
- cannot also use `mut`
```rust
let mut spaces = " "; 
spaces = spaces.len();
```
result:
```rust
$ cargo run Compiling variables v0.1.0 (file:///projects/variables) error[E0308]: mismatched types 
--> src/main.rs:3:14 
  | 
2 | let mut spaces = " "; 
  | ----- expected due to this value 
3 | spaces = spaces.len(); 
  | ^^^^^^^^^^^^ expected `&str`, found `usize` For more information about this error, try `rustc --explain E0308`. error: could not compile `variables` (bin "variables") due to 1 previous error

> [!NOTE]
> ```