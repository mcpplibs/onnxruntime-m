#include <mwrap/onnxruntime/macros.hpp>
import std;
import mcpplibs.mwrap.onnxruntime;

static_assert(std::is_same_v<decltype(Ort::SessionOptions{}), Ort::SessionOptions>);
static_assert(ORT_API_VERSION == 25);
int main() {
    Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "header-module-mix");
    return OrtGetApiBase() && OrtGetApiBase()->GetApi(ORT_API_VERSION) ? 0 : 1;
}
