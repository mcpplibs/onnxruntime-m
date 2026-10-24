Detailed usage and background. See the [README](../README.md) for the current candidate quickstart and support boundary.

# onnxruntime-m

ONNX Runtime **1.25.1** C and C++ APIs through `mcpplibs.mwrap` modules.
Upstream names remain unchanged: `Ort::Env`, `Ort::Session`, `Ort::Value`, and
the C API retain their original namespaces and types.

```toml
[dependencies."mcpplibs.mwrap"]
onnxruntime = "1.25.1"

[target.x86_64-linux-gnu]
cxx_runtime = "toolchain-coupled"
```

```cpp
import mcpplibs.mwrap.onnxruntime;
Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "example");
```

The Linux official SDK itself loads libstdc++. GCC applications should use the
toolchain-coupled C++ runtime shown above to share one implementation. The SDK
provider supplies its declared runtime closure; no host library search is used.

The package depends on `compat.onnxruntime`, which supplies the matching official
CPU SDK. Initial targets are Linux x86_64 with glibc, Windows x86_64 with the MSVC
ABI, and macOS arm64. GPU execution providers, musl and MinGW require separate
SDK builds and are not supplied by this version.

## Quickstart template

```sh
mcpp new inference --template mcpplibs.mwrap.onnxruntime@1.25.1
cd inference
mcpp run
```

The template contains a reproducible ONNX Identity model and verifies real CPU
inference. It needs no external model download or device.

`import mcpplibs.mwrap.onnxruntime.macros;` exposes the API version as
`mcpplibs::mwrap::onnxruntime::macros::ORT_API_VERSION`. Original preprocessing
macros, including `ORT_TSTR`, remain available through
`#include <mwrap/onnxruntime/macros.hpp>` **before** imports. A preprocessing macro
still expands inside a qualified identifier; use the mapping and raw-macro forms
in separate contexts.

The root also exposes the CPU provider factory, plugin EP API declarations,
`Ort::Custom` lightweight custom-op types and `onnxruntime::ProviderOptions`.
API availability does not install an execution provider that is absent from the CPU SDK.

Configuration keys follow the SDK's separate-header grouping:

```cpp
import mcpplibs.mwrap.onnxruntime;
import mcpplibs.mwrap.onnxruntime.config;
Ort::SessionOptions options;
options.AddConfigEntry(kOrtSessionOptionsConfigDisablePrepacking, "1");
```

The config module preserves global key names and pointer types. Upstream gives
these header variables internal linkage, which GCC cannot export directly, so
the module supplies equivalent inline constants. Use either this module or the
raw config headers in a translation unit; combining both creates duplicate key
names. Raw config headers can be mixed with the root module, as the tests verify.

## Development

Use mcpp 2026.10.24.1 or newer. Tests exercise module-only inference, output shape
and values, and header/module coexistence. `tools/generate_model.py` regenerates
the checked-in model, and `tools/generate_exports.py <sdk-include-directory>`
regenerates exports from Clang's declaration AST. SDK source pins and the public
declaration inventory live under `upstream/`.

For an unpublished provider, use a local `compat` index during development, then
run `mcpp test --toolchain llvm@23.1.3` and `mcpp test --toolchain gcc@16.1.0`.
`python3 tools/test_template.py --index /path/to/mcpp-index` runs the actual mcpp
template renderer and builds/runs the generated project against the candidate.

The wrapper is MIT licensed. The SDK is distributed separately with Microsoft's
MIT license and its `ThirdPartyNotices.txt`.
