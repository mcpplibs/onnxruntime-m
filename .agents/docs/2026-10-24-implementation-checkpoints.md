# ONNX Runtime mwrap implementation checkpoints

## CPU interface checkpoint

- Upstream official SDK: 1.25.1, hashes recorded in upstream/sources.lock.toml.
- Exports: 277 C declarations/enumerators and 107 public Ort declarations from Clang AST.
- LLVM 23.1.3: module inference and header coexistence, 2 passed.
- GCC 16.1.0: module inference and header coexistence, 2 passed.
- Actual mcpp new/list-templates followed by generated project build/run passed.
- Linux SDK runtime closure requires declared gcc-runtime; GCC consumers use toolchain-coupled C++ runtime.
- Provider candidate: mcpp-index-mwrap/pkgs/c/compat.onnxruntime.lua.
- Pending: C API/header inventory completion, isolated deployment, Windows/macOS CI, release/index consumption, remote PR.
- Remote organization creation currently refused for GitHub identity speak-agent (403); local implementation continues.
