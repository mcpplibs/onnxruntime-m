#!/usr/bin/env python3
"""Write a small ONNX Identity model without requiring Python ONNX packages."""
from pathlib import Path


def varint(value):
    out = bytearray()
    while value > 127:
        out.append((value & 127) | 128)
        value >>= 7
    out.append(value)
    return bytes(out)


def field(number, value):
    if isinstance(value, int):
        return varint(number << 3) + varint(value)
    if isinstance(value, str):
        value = value.encode()
    return varint((number << 3) | 2) + varint(len(value)) + value


def identity_model():
    shape = field(1, field(1, 3))
    tensor_type = field(1, 1) + field(2, shape)
    def value_info(name):
        return field(1, name) + field(2, field(1, tensor_type))
    node = field(1, "x") + field(2, "y") + field(4, "Identity")
    graph = field(1, node) + field(2, "mwrap_identity")
    graph += field(11, value_info("x")) + field(12, value_info("y"))
    return field(1, 8) + field(2, "mwrap-fixture") + field(7, graph) + field(8, field(2, 13))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    model = identity_model()
    (root / "tests/fixtures/identity.onnx").write_bytes(model)
    initializer = ", ".join(f"0x{x:02x}" for x in model)
    (root / "templates/inference/src/model.hpp").write_text(
        "#pragma once\ninline constexpr unsigned char identity_model[] = {" + initializer + "};\n")
    (root / "tests/fixtures/model.hpp").write_text(
        "#pragma once\ninline constexpr unsigned char identity_model[] = {" + initializer + "};\n")
