# onnxruntime-m

> ONNX Runtime 1.25.1 C/C++ API 的 C++23 模块封装，保留 Ort:: 名称。

[English](README.md) · **简体中文** · [Upstream](https://github.com/microsoft/onnxruntime) · [Releases](https://github.com/mcpplibs/onnxruntime-m/releases) · [mcpp](https://github.com/mcpp-community/mcpp) · [Index](https://github.com/mcpplibs/mcpp-index)

[![C++23](https://img.shields.io/badge/C%2B%2B-23-blue.svg)](https://en.cppreference.com/w/cpp/23)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/mcpplibs/onnxruntime-m/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/mcpplibs/onnxruntime-m/actions/workflows/ci.yml)

## 模块

- `import mcpplibs.mwrap.onnxruntime;`: Ort:: 与 C 推理 API
- `import mcpplibs.mwrap.onnxruntime.config;`: 会话与运行时配置键
- `import mcpplibs.mwrap.onnxruntime.macros;`: API 版本宏映射

> More Modules API -> [模块与 API](docs/usage.md)

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
