# onnxruntime-m

> ONNX Runtime 1.25.1 C/C++ APIs as C++23 modules; Ort:: names are preserved.

**English** · [简体中文](README.zh.md)

Use mcpp **2026.10.24.1**. The new mwrap identity becomes installable after index publication.

## Quick start

```sh
mcpp new inference --template mcpplibs.mwrap.onnxruntime@1.25.1
cd inference
mcpp run
```

```toml
[dependencies]
mcpplibs.mwrap.onnxruntime = "1.25.1"
```

## Existing projects

```cpp
import mcpplibs.mwrap.onnxruntime;
int main() { Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "example"); }
```

Linux GCC consumers set `cxx_runtime = "toolchain-coupled"` in `[target.x86_64-linux-gnu]` for the SDK exception runtime.

## Scope

Official CPU SDK: Linux x86_64 glibc, Windows x86_64 MSVC ABI, macOS ARM64.
GPU, musl and MinGW need separate SDKs. The template executes an embedded Identity model.
`.config` exposes configuration keys; `.macros` maps API version. Text macros use `<mwrap/onnxruntime/macros.hpp>` before imports.

## Documentation

[Usage and mixing limits](docs/usage.md) · [SDK provenance](upstream) · [Tests](tests) · [MIT](LICENSE)
The SDK retains its MIT license and ThirdPartyNotices.txt.
