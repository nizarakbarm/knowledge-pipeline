## Overview
- eBPF directly from Python
- use LLVM object files [IR layer—llvmlite.ir — llvmlite 0.47.0dev0+39.gbf28f75.dirty documentation](https://llvmlite.readthedocs.io/en/latest/user-guide/ir/index.html) for IR generation)
- support
	- maps
	- helpers
	- global definitions for BPF
- companion project: [pylibbpf](https://github.com/pythonbpf/pylibbpf)[GitHub - pythonbpf/pylibbpf: Python Bindings for libbpf](https://github.com/pythonbpf/pylibbpf) (bindings required for object loading and execution)
## Dependencies
- bpftool
- clang
- Python >= 3.8
- pylibbpf
```bash
pip install pythonbpf pylibbpf
```
## Trying
### Opensuse
- Install
```
zypper install -y bpftool clang
zypper addrepo -f https://download.opensuse.org/repositories/devel:/tools:/compiler/16.0/ devel_tools_compiler
zypper --gpg-auto-import-keys ref
zypper install llvm21 clang21 lld21 libclang-cpp2
pip install pythonbpf pylibbpf ctypeslib2
```
- Generate the vmlinux.py
```bash
tools/vmlinux-gen.py
```
- Copy this to `BCC-Examples/`
```bash
cp vmlinux.py BCC-Examples/
```
![[Pasted image 20260209200159.png]]
![[Pasted image 20260209200326.png]]