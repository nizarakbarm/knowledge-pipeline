# Rust Best Practices

Guide for writing idiomatic Rust code based on Apollo GraphQL's best practices handbook.

## Use When

1. Writing new Rust code or functions
2. Reviewing or refactoring existing Rust code
3. Deciding between borrowing vs cloning or ownership patterns
4. Implementing error handling with Result types
5. Optimizing Rust code for performance
6. Writing tests or documentation for Rust projects

## Ownership & Borrowing

### Prefer Borrowing Over Cloning
```rust
// Good: Borrow
fn process(items: &[Item]) { ... }

// Bad: Clone unnecessarily
fn process(items: Vec<Item>) { ... }
```

### Use `Arc` for Shared Ownership
```rust
use std::sync::Arc;

let data = Arc::new(vec![1, 2, 3]);
let data2 = Arc::clone(&data);
```

### Minimize `mut` Usage
```rust
// Good: Functional style
let doubled: Vec<i32> = numbers.iter().map(|n| n * 2).collect();

// Avoid: Mutable state
let mut doubled = Vec::new();
for n in numbers {
    doubled.push(n * 2);
}
```

## Error Handling

### Use `Result` for Fallible Operations
```rust
fn parse_config(path: &str) -> Result<Config, ConfigError> {
    let content = std::fs::read_to_string(path)?;
    // ...
}
```

### Define Custom Error Types
```rust
#[derive(Debug, thiserror::Error)]
enum AppError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Parse error: {0}")]
    Parse(#[from] serde_json::Error),
}
```

### Use `?` Operator Liberally
```rust
fn process() -> Result<(), AppError> {
    let data = read_file()?;
    let parsed = parse_data(&data)?;
    save_result(parsed)?;
    Ok(())
}
```

## Types & Traits

### Use Newtypes for Type Safety
```rust
struct UserId(u64);
struct OrderId(u64);

fn find_user(id: UserId) -> Option<User> { ... }
// Cannot accidentally pass OrderId
```

### Implement Common Traits
```rust
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct Point {
    x: i32,
    y: i32,
}
```

### Use Trait Bounds Wisely
```rust
fn process<T: Display + Serialize>(item: T) -> String { ... }

// Or use where clauses for complex bounds
fn process<T>(item: T) -> String
where
    T: Display + Serialize,
{ ... }
```

## Performance

### Avoid Unnecessary Allocations
```rust
// Good: Zero-copy where possible
fn first_word(s: &str) -> &str {
    s.split_whitespace().next().unwrap_or(s)
}
```

### Use Iterators Instead of Loops
```rust
// Good: Iterator chains
let sum: i32 = numbers.iter().filter(|n| **n > 0).sum();

// Avoid: Manual loops
let mut sum = 0;
for n in numbers {
    if n > 0 {
        sum += n;
    }
}
```

### Choose Collections Wisely
- `Vec` - Sequential access, dynamic size
- `HashMap` - Key-value lookup
- `BTreeMap` - Ordered key-value
- `HashSet` - Unique items, membership testing
- `VecDeque` - Queue operations

## Testing

### Unit Tests in Same File
```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_add() {
        assert_eq!(add(2, 2), 4);
    }
}
```

### Use Property-Based Testing
```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn test_reverse_reverse(a: Vec<i32>) {
        let reversed: Vec<i32> = a.clone().into_iter().rev().collect();
        let double_reversed: Vec<i32> = reversed.into_iter().rev().collect();
        prop_assert_eq!(a, double_reversed);
    }
}
```

## Async/Await

### Use `tokio` for Runtime
```rust
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let result = fetch_data().await?;
    println!("{}", result);
    Ok(())
}
```

### Spawn Tasks for Parallelism
```rust
let handle = tokio::spawn(async {
    process_item(item).await
});

let result = handle.await??;
```

## Documentation

### Document Public APIs
```rust
/// Calculates the factorial of a number.
///
/// # Examples
///
/// ```
/// assert_eq!(factorial(5), 120);
/// ```
///
/// # Panics
///
/// Panics if `n` > 20 due to overflow.
pub fn factorial(n: u32) -> u32 { ... }
```

## Common Patterns

### Builder Pattern
```rust
let config = Config::builder()
    .host("localhost")
    .port(8080)
    .timeout(Duration::from_secs(30))
    .build()?;
```

### RAII with Drop
```rust
struct TempFile {
    path: PathBuf,
}

impl Drop for TempFile {
    fn drop(&mut self) {
        let _ = std::fs::remove_file(&self.path);
    }
}
```

### Type State Pattern
```rust
struct Uninitialized;
struct Ready;

struct Connection<State> {
    state: State,
}

impl Connection<Uninitialized> {
    fn new() -> Self { ... }
    fn connect(self) -> Connection<Ready> { ... }
}

impl Connection<Ready> {
    fn query(&self, sql: &str) -> Result<Rows> { ... }
}
```
