# Clean Architecture Principles

Clean Architecture principles and best practices from Robert C. Martin's book. Use when designing software systems, reviewing code structure, or refactoring applications to achieve better separation of concerns.

## Core Principles

### Dependency Rule
Dependencies must point inward. Inner layers should not know about outer layers.

```
[Entities] <-- [Use Cases] <-- [Interface Adapters] <-- [Frameworks & Drivers]
```

### Layer Responsibilities

**Entities**: Enterprise-wide business rules
- Plain objects with business logic
- No framework dependencies
- No persistence awareness

**Use Cases**: Application-specific business rules
- Orchestrate entities
- Define input/output ports
- No presentation logic
- No framework imports

**Interface Adapters**: Convert data for use cases
- Controllers (thin)
- Presenters (format data)
- Gateways (abstract external systems)
- Mappers (translate between layers)

**Frameworks & Drivers**: External concerns
- Web frameworks
- Databases
- UI
- External APIs

## Key Rules

### No Framework Imports in Domain
Entities and use cases must not import framework-specific code.

### Interface Ownership
Interfaces belong to the layer that uses them, not the layer that implements them.

### Stable Abstractions
Abstract classes and interfaces should be stable. Concrete implementations can change.

### Data Crossing Boundaries
Data must be in simple structures (DTOs) when crossing layer boundaries.

## Testing Strategy

### Test Pyramid
- **Unit Tests**: Test entities and use cases in isolation
- **Integration Tests**: Test interface adapters
- **E2E Tests**: Test complete flows through frameworks

### Testable Design
- Dependency injection
- Interface-based design
- No static/singleton dependencies in domain

## Component Principles

### Common Reuse Principle
Classes that are used together should be packaged together.

### Common Closure Principle
Classes that change together should be packaged together.

### Stable Dependencies Principle
Depend on stable packages. A package should be more stable than the packages it depends on.

### Stable Abstractions Principle
Stable packages should be abstract. Unstable packages should be concrete.

## Anti-Corruption Layer

When integrating with external systems:
- Create adapter/gateway interfaces
- Translate external models to domain models
- Isolate domain from external changes

## References

- Robert C. Martin - "Clean Architecture"
- The Dependency Rule
- Screaming Architecture
- The Humble Object Pattern
