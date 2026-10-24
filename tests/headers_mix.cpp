#include <mwrap/onnxruntime/macros.hpp>
#include <onnxruntime_session_options_config_keys.h>
import std;
import mcpplibs.mwrap.onnxruntime;

static_assert(std::is_same_v<decltype(Ort::SessionOptions{}), Ort::SessionOptions>);
static_assert(ORT_API_VERSION == 25);
int main() {
    Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "header-module-mix");
    if (std::string_view(kOrtSessionOptionsConfigDisablePrepacking) != "session.disable_prepacking") return 2;
    return OrtGetApiBase() && OrtGetApiBase()->GetApi(ORT_API_VERSION) ? 0 : 1;
}
