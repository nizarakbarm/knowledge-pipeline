A complete pipeline to write, compile, and load eBPF programs in Python
1. Python Source Code
	- Write BPF prog with decorators in Python
		- @bpf
		- @map
		- @section
		- @bpfglobal
	- Maps (hash maps), helpers (e.g., `ktime`, `deref`), and tracepoints in forms of Python constructs (syntax close to standard python)
2. AST Generation
	- python `ast` > parses the source code into an Abstract Syntax Tree (AST)
	- Decorators and anotations are captured (for BPF maps, tracepoints, and global variables)
3. LLVM IR Emission
	- AST -> transformed -> LLVM intermediate Representation (IR) using `llvmlite`
	- IR captures BPF maps, control flow, assignments, and calls to helper functions
	- Debug info -> emitted for inspection
4. LLVM Object File Compilation
	- LLVM IR (.ll) is compiled into a BPF target object file (`.o`) using `llc -march=bpf -O2`
	- Produces a kernel-loadable ELF object file containing the BPF bytecode
5. libbpf integration (via pylibbpf)
	- the compiled object file -> loaded into the kernel by using `pylibbpf`
	- Maps, tracepoints, and program section are initialized, and helper functions are resolved
	- programs are atteched to kernel hooks (e.g., syscalls) for execution
6. Execution in kernel
	- kernel executes the loaded eBPF
	- hash maps, helpers, and global variables behave as defined in  the Python source
	- Output can be read via BPF maps, helper functions, or trace printing

This eliminates the need for embedding C code in Python (as in BCC) allowing full python tooling support to generate true BPF object files ready for kernel execution