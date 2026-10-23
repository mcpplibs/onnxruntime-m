module;
#include <onnxruntime_c_api.h>
namespace mwrap_onnxruntime_detail {
inline constexpr unsigned api_version = ORT_API_VERSION;
}
#undef ORT_API_VERSION

export module mcpplibs.mwrap.onnxruntime.macros;

export namespace mcpplibs::mwrap::onnxruntime::macros {
inline constexpr unsigned ORT_API_VERSION = mwrap_onnxruntime_detail::api_version;
}
