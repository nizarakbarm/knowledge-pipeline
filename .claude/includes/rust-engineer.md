# Rust Systems Programming

Use when building Rust applications requiring memory safety, systems programming, or zero-cost abstractions. Covers ownership patterns, lifetimes, traits, async/await with tokio.

## Ownership Patterns

### Move Semantics
```rust
let s1 = String::from("hello");
let s2 = s1;  // s1 moved to s2
// println!("{}", s1);  // Error! s1 no longer valid
```

### Copy Types
```rust
let x = 5;
let y = x;  // Copy (implicit)
println!("{}", x);  // OK! i32 implements Copy
```

### Borrowing Rules
1. One mutable reference OR any number of immutable references
2. References must always be valid
3. No dangling references

```rust
fn main() {
    let mut s = String::from("hello");
    
    let r1 = &s;  // Immutable borrow
    let r2 = &s;  // Immutable borrow (OK)
    println!("{} {}", r1, r2);
    
    let r3 = &mut s;  // Mutable borrow (OK after r1, r2 dropped)
    r3.push_str(" world");
}
```

## Lifetimes

### Explicit Lifetimes
```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

### Lifetime Elision Rules
```rust
// These are equivalent:
fn first_word(s: &str) -> &str { ... }
fn first_word<'a>(s: &'a str) -> &'a str { ... }
```

### Static Lifetime
```rust
let s: &'static str = "This lives for the entire program";
```

## Traits

### Defining Traits
```rust
trait Drawable {
    fn draw(&self);
    fn bounds(&self) -> Rect {
        // Default implementation
        Rect::default()
    }
}
```

### Implementing Traits
```rust
struct Circle { radius: f64 }

impl Drawable for Circle {
    fn draw(&self) {
        println!("Drawing circle with radius {}", self.radius);
    }
}
```

### Trait Bounds
```rust
fn draw_all<T: Drawable>(items: &[T]) {
    for item in items {
        item.draw();
    }
}

// Multiple bounds
fn process<T: Drawable + Clone + Send>(item: T) { ... }
```

### Associated Types
```rust
trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
}

impl Iterator for Counter {
    type Item = u32;
    fn next(&mut self) -> Option<u32> { ... }
}
```

## Smart Pointers

### Box
```rust
let b = Box::new(5);  // Heap allocation
```

### Rc (Reference Counted)
```rust
use std::rc::Rc;

let data = Rc::new(vec![1, 2, 3]);
let data2 = Rc::clone(&data);
```

### Arc (Atomic Reference Counted)
```rust
use std::sync::Arc;

let data = Arc::new(Mutex::new(0));
let data2 = Arc::clone(&data);
```

## Concurrency

### Threads
```rust
use std::thread;

let handle = thread::spawn(|| {
    // Do work in new thread
    42
});

let result = handle.join().unwrap();
```

### Channels
```rust
use std::sync::mpsc;

let (tx, rx) = mpsc::channel();

tx.send(42).unwrap();
let received = rx.recv().unwrap();
```

### Mutex
```rust
use std::sync::Mutex;

let m = Mutex::new(5);
{
    let mut num = m.lock().unwrap();
    *num = 6;
}  // Lock released here
```

## Async/Await with Tokio

### Basic Runtime
```rust
#[tokio::main]
async fn main() {
    let result = async_operation().await;
    println!("{}", result);
}
```

### Spawning Tasks
```rust
let handle = tokio::spawn(async {
    // Async work
    42
});

let result = handle.await.unwrap();
```

### Async Functions
```rust
async fn fetch_data(url: &str) -> Result<String, reqwest::Error> {
    let response = reqwest::get(url).await?;
    let text = response.text().await?;
    Ok(text)
}
```

### Select
```rust
tokio::select! {
    result = task1 => println!("Task 1: {:?}", result),
    result = task2 => println!("Task 2: {:?}", result),
}
```

## Unsafe Rust

### When to Use
- FFI (Foreign Function Interface)
- Raw pointers for performance
- Implementing low-level data structures

### Rules
```rust
unsafe {
    // Dereference raw pointer
    let data = *raw_ptr;
    
    // Call unsafe function
    dangerous_function();
    
    // Access/modify mutable static
    COUNTER += 1;
}
```

### Requirements
- Mark unsafe functions with `unsafe fn`
- Document invariants that must be upheld
- Keep unsafe blocks as small as possible
- Encapsulate unsafe in safe abstractions

## Macros

### Declarative Macros
```rust
macro_rules! vec {
    ($($x:expr),*) => {
        {
            let mut temp_vec = Vec::new();
            $(
                temp_vec.push($x);
            )*
            temp_vec
        }
    };
}
```

### Procedural Macros
```rust
#[derive(Debug, Clone)]
struct Point { x: i32, y: i32 }
```

## FFI (Foreign Function Interface)

### Calling C from Rust
```rust
extern "C" {
    fn abs(input: i32) -> i32;
}

fn main() {
    unsafe {
        println!("Absolute value of -3: {}", abs(-3));
    }
}
```

### Calling Rust from C
```rust
#[no_mangle]
pub extern "C" fn add(a: i32, b: i32) -> i32 {
    a + b
}
```
