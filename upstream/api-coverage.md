# Official CPU SDK header coverage

The source of truth is the official 1.25.1 CPU SDK pinned in sources.lock.toml.
tools/generate_exports.py records enabled declarations from Clang's semantic
AST. Its --check mode verifies committed exports and inventory without pruning
compiler failures. Methods and overloads remain members of the original exported
classes; the inventory counts top-level names, not every member function.

| SDK surface | Module surface |
|---|---|
| onnxruntime_c_api.h, including its unguarded onnxruntime_ep_c_api.h continuation | Root: C types, enumerators, API tables and callback typedefs |
| onnxruntime_cxx_api.h and onnxruntime_cxx_inline.h | Root: original public Ort declarations and their methods |
| cpu_provider_factory.h | Root: original CPU registration function, tested against the actual SDK |
| onnxruntime_lite_custom_op.h | Root: original Ort::Custom types and factories |
| provider_options.h | Root: original onnxruntime::ProviderOptions aliases |
| core/providers/custom_op_context.h and resource.h | Root: original custom-op context and resource offsets |
| env/run/session config keys and EP metadata keys | Separate .config module, preserving global names and pointer types |
| onnxruntime_float16.h | Original public Ort float16 types through the C++ API; their implementation namespace remains an implementation dependency |

The SDK's configuration keys have internal linkage. GCC rejects exporting those
variables directly. The .config module supplies equivalent inline constant
pointers; combining it with the same raw config headers would introduce two
entities with the same names. As upstream's C++ API header itself does not
include those separate key headers, the root does not re-export .config. Both
module-only config use and raw-config-header/root-module coexistence are tested.

Function-like/preprocessing-control macros require the compatibility header
before import. ORT_API_VERSION additionally has a typed mapping in .macros.
The default module uses the SDK's normal API initialization mode, not a caller's
later preprocessing changes. Internal detail namespaces and implementation-only
float16 helpers are not promoted to public module APIs.

The SDK is CPU-only. EP API declarations and resource offsets do not supply GPU
provider binaries. No claim is made that a CPU SDK can execute those providers.
