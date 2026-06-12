---
created: 2026-06-12
up:
  - "[[Tetragon Overview]]"
  - "[[eBPF MOC]]"
related:
  - "[[Tetragon Events]]"
  - "[[Tetragon TracingPolicy - Hook Points]]"
  - "[[Tetragon TracingPolicy - Argument Types]]"
  - "[[Tetragon TracingPolicy - Example]]"
  - "[[eBPF (extended Berkeley Packet Filter)]]"
  - "[[eBPF Concept - BPF_CORE_READ]]"
  - "[[Kubernetes]]"
in:
  - "[[Things]]"
tags:
  - concept
  - tetragon
  - ebpf
  - security
  - kubernetes
  - tracing-policy
  - enforcement
---

# Tetragon TracingPolicy

## Core Idea

**TracingPolicy** is a [[Kubernetes]] Custom Resource (CRD) that defines *what* kernel and userspace functions to observe and *how* to react when specific conditions are met. It is the primary input mechanism for [[Tetragon Overview|Cilium Tetragon]]'s eBPF-based security enforcement engine — transforming the Linux kernel into a programmable, identity-aware security plane.

Where [[Tetragon Events]] describes what Tetragon *outputs*, TracingPolicy describes what it *watches* and *does*.

## Key Principles

### In-Kernel Selectivity

All filtering logic executes within the [[eBPF (extended Berkeley Packet Filter)|eBPF]] layer — high-volume noise is discarded before reaching userspace. This eliminates context-switch overhead and enables enforcement *before* a malicious syscall completes.

### Hook Point Versatility

Five instrumentation families:

| Hook Type | Target | Stability |
|-----------|--------|-----------|
| **kprobes** | Any kernel function | Dynamic (may break across versions) |
| **tracepoints** | Static kernel tracepoints | Stable ABI |
| **uprobes** | User-space functions | Binary-dependent |
| **USDTs** | Application-defined probes | Application ABI |
| **LSM BPF** | Linux Security Module hooks | Kernel security framework |

### Enforcement Actions

| Action | Effect | Use Case |
|--------|--------|----------|
| **Sigkill** | Terminate process synchronously in-kernel | Kill malicious process mid-syscall |
| **Override** | Inject error return value | Block syscall with -EPERM |
| **Post** | Emit observability event | Logging without enforcement |

### Selector Semantics

- **AND** within a single selector (all conditions must match)
- **Short-circuit OR** between multiple selectors (first match wins)
- Max 5 selectors per hook; no filters = match all; no action = Post default

### Kubernetes Identity Awareness

Every kernel event joins with cluster metadata — rules expressed in workload identity (Namespace, Pod, Labels, Container) rather than raw PIDs or IPs.

## Hook Types

Five instrumentation families: kprobes, tracepoints, uprobes, USDTs, and LSM BPF — spanning kernel-space and user-space. LSM BPF is the only hook type enforcing *before* operation completion (TOCTOU-free). Includes BTF attribute resolution, return value tracking with socket attribution, reusable function lists, and selector macros.

See: [[Tetragon TracingPolicy - Hook Points]]

## Argument Type Catalog

Eight categories spanning integers, strings, network, buffers, filesystem, credentials, BPF internals, and special types — each with its own operator set and security use cases. Critical gotchas: `sizeArgIndex` is 1-based, `maxData` silently truncates unmatched data, kernel version gates for `SubString` (≥6.17) and full path resolution (≥5.3).

See: [[Tetragon TracingPolicy - Argument Types]]

## Selectors

Selectors define per-hook in-kernel BPF filtering logic. A selector matches when **all** its filters match (AND). Multiple selectors evaluate as **short-circuit OR** (first match's action fires). Max 5 selectors per hook.

### Filter Types

| Filter | Description | Key Operators |
|--------|-------------|---------------|
| **matchArgs** | Function argument values | Equal, NotEqual, Prefix, Postfix, Mask, FileType |
| **matchData** | Kernel data structure fields (current_task, pt_regs) | Equal, NotEqual, Prefix, Postfix, GreaterThan |
| **matchReturnArgs** | Function return values | Equal, NotEqual, Prefix, Postfix |
| **matchPIDs** | Process IDs with namespace awareness | In, NotIn + followForks, isNamespacePID |
| **matchBinaries** | Executable paths | In, NotIn, Prefix, NotPrefix, Postfix, NotPostfix + followChildren |
| **matchParentBinaries** | Parent process binary (requires `--parents-map-enabled`) | In, NotIn, Prefix, Postfix |
| **matchNamespaces** | Linux namespace IDs (7 types, max 4 values) | In, NotIn + `host_ns` keyword |
| **matchCapabilities** | Process capability sets (Effective/Inheritable/Permitted) | In, NotIn |
| **matchNamespaceChanges** | Runtime namespace transitions since exec | In with namespace type |
| **matchCapabilityChanges** | Runtime capability changes since exec | In with capability type |
| **matchWorkloads** | Kubernetes identity (host/pod/container) | hostSelector, podSelector, containerSelector |

**kubectl exec detection**: `matchPIDs` with `NotIn + isNamespacePID: true + values: [1]` — in-container processes with PID != 1 are not children of init.

**Script caveat**: `matchBinaries` matches the *interpreter* path (e.g., `/usr/bin/python3`), not the script path.

### Action Types

| Action | Mechanism | Use Case |
|--------|-----------|----------|
| **Sigkill** | Synchronous process termination in eBPF | Kill malicious process before syscall completes |
| **Signal** | Send arbitrary signal via `argSig` | Graceful shutdown (SIGTERM) or debug (SIGUSR1) |
| **Override** | Inject error return via `argError` (requires `CONFIG_BPF_KPROBE_OVERRIDE`) | Block syscall without killing process |
| **GetUrl** | HTTP GET request via `argUrl` | Canary/thinkst triggers |
| **DnsLookup** | DNS lookup via `argFqdn` | Canary triggers |
| **Post** | Emit event with `rateLimit`, `kernelStackTrace`, `userStackTrace` | Default observability action |
| **NoPost** | Suppress event emission | Silence expected events in multi-selector chains |
| **FollowFD/UnfollowFD/CopyFD** | BPF map FD tracking (deprecated, removed in 1.5) | File descriptor-to-path resolution |
| **TrackSock/UntrackSock** | Socket-to-process attribution BPF maps | Async network event attribution |
| **NotifyEnforcer** | External enforcer notification | Distributed enforcement architectures |

**Post rate limiting**: `rateLimit` in s/m/h with `rateLimitScope` (thread/process/global). Stack tracing: `kernelStackTrace` and `userStackTrace` flags capture call chains. Requires `--expose-stack-addresses` for address visibility.

## Kubernetes Filtering

In-kernel filtering by Kubernetes identity reduces overhead (discard non-matching events before userspace copy) and prevents race conditions (enforcement before syscall completion).

### TracingPolicyNamespaced

Separate CRD restricted to a single namespace. Same structure as `TracingPolicy` but scoped at the API level — namespace admins cannot create cluster-wide policies. Non-null `hostSelector` on a namespaced policy causes a validation error.

### PodSelector

Standard Kubernetes label selector syntax (`matchLabels`, `matchExpressions` with In/NotIn/Exists/DoesNotExist). Targets specific workload groups within the cluster.

### containerSelector

Secondary filter on podSelector results. Supported fields: `name` (container name), `repo` (image repository). Enables surgical targeting: "only the nginx container in app=web pods."

### hostSelector

`{}` matches all host workloads; `null` (default) matches none with other selectors, or all when all selectors are null.

### Filtering Semantics

All selectors null = match all workloads. `hostSelector: {}` alone = match all host workloads only. `podSelector: {}` = match all pod workloads only. Container scope always narrows pod scope.

OCI runtime hooks required for guaranteed pre-container-start enforcement. Without them, Tetragon applies policies in best-effort manner via k8s API server.

## Enforcement Modes

Three modes: **monitoring** (enforcement actions elided), **enforcement** (actions active), **monitor_only** (no enforcement actions in policy — cannot be escalated, a one-way safety lock).

Three setting methods (increasing priority):
1. **In-policy**: `spec.options name: policy-mode value: monitor/enforcement`
2. **Load-time**: `tetra tracingpolicy add --mode monitor policy.yaml`
3. **Runtime**: `tetra tp set-mode --namespace <ns> <name> <mode>`

`tetra tracingpolicy list` shows MODE column (`monitor_only`/`monitoring`/`enforcement`) plus NPOST/NENFORCE/NMONITOR counters. Setting `monitor_only` to enforcement at runtime errors. Loading `monitor_only` always succeeds with a warning.

## Tags

Optional string arrays at the hook level for event categorization. Max 16 tags per hook. Standard namespaced tags: `observability.filesystem`, `observability.privilege_escalation`, `observability.process`. User-defined tags supported with no naming restrictions. Tags propagate into event JSON output for SIEM/SOC filtering.

## Policy Options

`spec.options` array of name/value pairs passed to hooks that support them:

| Option | Default | Effect |
|--------|---------|--------|
| `disable-kprobe-multi` | `false` | Force standard kprobe attachment instead of multi-link batch API |
| `disable-uprobe-multi` | `false` | Force standard uprobe attachment instead of multi-link batch API |

Options are scoped per-spec-file. Multi-link is transparent to policy semantics — disabling affects only the kernel attachment mechanism, not filtering behavior.

## Example Walkthrough

Minimal policy hooking `fd_install` with Sigkill action on `/tmp/tetragon` — demonstrating the four-layer architecture (Kubernetes identity → hook definition → selectors → event observation) and the kill-before-exposure enforcement model where the process is terminated before the file descriptor is installed.

See: [[Tetragon TracingPolicy - Example]]

## Connections

### Atomic Splits
- **[[Tetragon TracingPolicy - Hook Points]]** — detailed breakdown of kprobes, tracepoints, uprobes, USDTs, LSM BPF hooks, BTF resolution, return values, function lists, and selector macros
- **[[Tetragon TracingPolicy - Argument Types]]** — complete argument type catalog with operators and security use cases
- **[[Tetragon TracingPolicy - Example]]** — fd_install walkthrough with four-layer architecture and kill-before-exposure analysis

- **[[Tetragon Overview]]** — parent entity: architecture, threat model, three pillars
- **[[Tetragon Events]]** — output side: what TracingPolicy hooks generate and how events are filtered/exported
- **[[eBPF (extended Berkeley Packet Filter)]]** — underlying technology enabling in-kernel policy execution
- **[[eBPF MOC]]** — broader eBPF knowledge index
- **[[eBPF Concept - BPF_CORE_READ]]** — related BTF-based kernel structure access pattern
- **[[Kubernetes]]** — identity context and CRD management interface
- **TOCTOU mitigation** — LSM hooks operate on kernel-resident state, closing race conditions
- **Domain sharding** — k8s/grpc/static isolation for deterministic multi-source policy management

## Applications

- **Runtime security enforcement** — kill processes executing unauthorized binaries or syscalls
- **Container escape detection** — `isNamespacePID` PID 1 filter catches `kubectl exec` injections
- **Network attribution** — TrackSock maps async network events to originating processes
- **Data exfiltration prevention** — redaction filters mask secrets before JSON export
- **Binary integrity verification** — IMA integration adds file hashes to security events
- **Zero-day response** — custom policies deploy independently of vendor release cycles
- **Supply chain security** — container image repo filtering blocks untrusted base images
- **Privilege escalation detection** — matchCapabilityChanges tracks runtime capability modifications

## Advanced Features

- **BTF attribute resolution**: dynamic nested kernel structure extraction without manual offsets
- **Selector macros**: reusable selector snippets across multiple hooks via `selectorsMacros`
- **Rate limiting**: thread/process/global throttling protects userspace from event floods
- **Enforcement mode toggles**: monitor → enforce for risk-free policy validation
- **Static loading**: local directory policies ensure early-boot protection
- **Generated function lists**: `generated_syscalls` and `generated_ftrace` auto-populate from kernel symbols

## Command Reference

```shell
tetra tracingpolicy domains
tetra tracingpolicy add --mode monitor policy.yaml
tetra tp set-mode --namespace <ns> <name> enforce
tetra tracingpolicy list
tetra tracingpolicy generate usdts --binary <path>
```

## Loading Methods

| Method | Command | Domain |
|--------|---------|--------|
| Kubernetes | `kubectl apply -f policy.yaml` | `k8s` |
| Kubernetes (namespaced) | `kubectl apply -n <ns> -f policy.yaml` | `k8s` |
| gRPC CLI | `tetra tracingpolicy add policy.yaml` | `grpc` |
| Static | `--tracing-policy=policy.yaml` daemon flag | `static` |

## Source

- Main documentation: https://tetragon.io/docs/concepts/tracing-policy/
- Example: https://tetragon.io/docs/concepts/tracing-policy/example/
- Argument types: https://tetragon.io/docs/concepts/tracing-policy/argument_types/
- Hook points: https://tetragon.io/docs/concepts/tracing-policy/hooks/
- Options: https://tetragon.io/docs/concepts/tracing-policy/options/
- Selectors: https://tetragon.io/docs/concepts/tracing-policy/selectors/
- Tags: https://tetragon.io/docs/concepts/tracing-policy/tags/
- Kubernetes filtering: https://tetragon.io/docs/concepts/tracing-policy/k8s-filtering/
- Enforcement mode: https://tetragon.io/docs/concepts/tracing-policy/mode/
- CRD Reference: https://tetragon.io/docs/reference/tracing-policy/
