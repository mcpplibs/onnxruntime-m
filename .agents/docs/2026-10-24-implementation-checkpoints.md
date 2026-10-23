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
- Organization repository creation is resolved through the existing authorized GitHub account; the default local account is unchanged.

## SDK deployment and native CI checkpoint

- An isolated MCPP_HOME with no ORT SDK successfully downloaded and installed the current SDK provider, then passed LLVM inference and header/module coexistence tests.
- The SDK provider is pinned to mcpp-index commit 3067e52abc0165b453ea3acac4022895ebf7d9bc for reproducible candidate CI.
- Native CI covers Linux GCC/LLVM, macOS arm64 and Windows MSVC ABI, including actual mcpp template rendering, build and execution.
- tools/test_candidate.py stages the candidate source and index routing outside the checkout; local --cold-sdk additionally verifies installation into a fresh home.
- Pending CI results, API inventory completion and release/index archive consumption remain release gates.
