# onnxruntime-m

ONNX Runtime **1.25.1** C/C++ APIs through C++23 modules, preserving `Ort::` and C API names.

## Quick start

Use mcpp **2026.10.24.1**. This candidate becomes available after index publication.

```sh
mcpp new inference --template mcpplibs.mwrap.onnxruntime@1.25.1
cd inference
mcpp run
```

The default template runs an embedded ONNX Identity model on the CPU and checks its output.

## Existing projects

```toml
[dependencies]
"mcpplibs.mwrap.onnxruntime" = "1.25.1"

[target.x86_64-linux-gnu]
cxx_runtime = "toolchain-coupled"
```

```cpp
import mcpplibs.mwrap.onnxruntime;
int main() {
    Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "example");
    return 0;
}
```

The Linux SDK loads libstdc++; GCC consumers use the runtime setting above to share one implementation.

## Scope

The official CPU SDK supports Linux x86_64 glibc, Windows x86_64 MSVC ABI and macOS arm64.
GPU providers, musl and MinGW need separate SDK builds. Provider API declarations do not install providers.

The `.config` submodule exposes configuration keys; `.macros` maps the API-version constant.
Raw macros use `<mwrap/onnxruntime/macros.hpp>` before imports. Mixing limits are documented below.

## Documentation

[Usage, macros and configuration](docs/usage.md) · [SDK provenance](upstream) ·
[Tests](tests) · [MIT](LICENSE)

The SDK carries its own MIT license and `ThirdPartyNotices.txt`.
