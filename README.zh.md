# onnxruntime-m

> ONNX Runtime 1.25.1 C/C++ API 的 C++23 模块封装，保留 Ort:: 名称。

[English](README.md) · **简体中文**

使用 mcpp **2026.10.24.1**。新 mwrap 身份在索引发布后可直接安装。

## 快速开始

```sh
mcpp new inference --template mcpplibs.mwrap.onnxruntime@1.25.1
cd inference
mcpp run
```

```toml
[dependencies]
mcpplibs.mwrap.onnxruntime = "1.25.1"
```

## 已有项目

```cpp
import mcpplibs.mwrap.onnxruntime;
int main() { Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "example"); }
```

Linux GCC 消费者在 `[target.x86_64-linux-gnu]` 设置 `cxx_runtime = "toolchain-coupled"`，共享 SDK 异常运行时。

## 支持范围

官方 CPU SDK：Linux x86_64 glibc、Windows x86_64 MSVC ABI、macOS ARM64。
GPU、musl、MinGW 需要独立 SDK；模板实际执行内嵌 Identity 模型。
`.config` 导出配置键，`.macros` 映射 API 版本；文本宏在 import 前包含 `<mwrap/onnxruntime/macros.hpp>`。

## 文档

[使用与混用限制](docs/usage.md) · [SDK 来源](upstream) · [测试](tests) · [MIT](LICENSE)
SDK 保留 MIT 许可证与 ThirdPartyNotices.txt。
