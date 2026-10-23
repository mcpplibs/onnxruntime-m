#!/usr/bin/env python3
"""Generate export-using declarations from Clang's public SDK declaration AST."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import tomllib


def generate(ast):
    declarations = ast.get("inner", [])
    namespaces = {name: [] for name in ("Ort", "Ort::Custom", "onnxruntime", "mwrap_onnxruntime_config_detail")}

    def find_namespaces(nodes, prefix=""):
        for node in nodes:
            if node.get("kind") != "NamespaceDecl":
                continue
            name = "::".join(filter(None, (prefix, node.get("name", ""))))
            if name in namespaces:
                namespaces[name].append(node)
            find_namespaces(node.get("inner", []), name)

    find_namespaces(declarations)
    kinds = {"CXXRecordDecl", "RecordDecl", "ClassTemplateDecl", "FunctionTemplateDecl",
             "FunctionDecl", "TypeAliasDecl", "TypeAliasTemplateDecl", "TypedefDecl", "EnumDecl", "VarDecl"}
    cpp, capi = {}, set()
    for path, extensions in namespaces.items():
        namespace_ids = {node["id"] for node in extensions}
        names = set()
        for namespace in extensions:
            for node in namespace.get("inner", []):
                name = node.get("name", "")
                if node.get("kind") not in kinds or not name.isidentifier() or node.get("isImplicit"):
                    continue
                # Ignore out-of-line definitions whose semantic owner is a
                # class or an internal namespace rather than this public scope.
                owner = node.get("parentDeclContextId")
                if owner and owner not in namespace_ids:
                    continue
                if node.get("kind") == "FunctionTemplateDecl" and any(
                        x.get("kind") == "CXXMethodDecl" for x in node.get("inner", [])):
                    continue
                names.add(name)
        cpp[path] = sorted(names)

    def collect_c(nodes):
        for node in nodes:
            if node.get("kind") == "LinkageSpecDecl":
                collect_c(node.get("inner", []))
                continue
            name = node.get("name", "")
            public_name = name.startswith(("Ort", "ONNX")) or name in {
                "GraphOptimizationLevel", "ExecutionMode", "ExecutionOrder", "RunAsyncCallbackFn",
                "CreateEpApiFactoriesFn", "ReleaseEpApiFactoryFn", "CustomOpContext", "ResourceOffset"}
            if public_name and node.get("kind") in kinds | {"TypedefDecl"}:
                capi.add(name)
                if node.get("kind") == "EnumDecl":
                    capi.update(x["name"] for x in node.get("inner", [])
                                if x.get("kind") == "EnumConstantDecl")
    collect_c(declarations)
    return sorted(capi), cpp


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sdk_include", type=Path)
    parser.add_argument("--clang", default="clang++")
    parser.add_argument("--check", action="store_true", help="fail if the committed inventory/exports differ")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    lock = tomllib.loads((root / "upstream/sources.lock.toml").read_text())
    for header in lock["onnxruntime"]["supplemental-headers"].values():
        digest = hashlib.sha256((root / header["path"]).read_bytes()).hexdigest()
        if digest != header["sha256"]:
            raise SystemExit(f"Supplemental upstream header differs: {header['path']}")
    config_headers = ("onnxruntime_env_config_keys.h", "onnxruntime_run_options_config_keys.h",
                      "onnxruntime_session_options_config_keys.h", "onnxruntime_ep_device_ep_metadata_keys.h")
    with tempfile.TemporaryDirectory(prefix="mwrap-ort-exports-") as temporary:
        directory = Path(temporary)
        probe = directory / "probe.cpp"
        probe.write_text("\n".join(f"#include <{header}>" for header in (
            "onnxruntime_cxx_api.h", "cpu_provider_factory.h",
            "provider_options.h", "onnxruntime_lite_custom_op.h",
            "core/providers/custom_op_context.h", "core/providers/resource.h")) +
            "\nnamespace mwrap_onnxruntime_config_detail {\n" +
            "\n".join(f"#include <{header}>" for header in config_headers) + "\n}\n")
        with (directory / "ast.json").open("w") as out:
            subprocess.run([args.clang, "-std=c++23", "-I", str(args.sdk_include), "-I", str(root / "upstream/include"),
                            "-Xclang", "-ast-dump=json", "-fsyntax-only", str(probe)],
                           stdout=out, check=True)
        with (directory / "ast.json").open() as source:
            capi, cpp = generate(json.load(source))
    config_keys = cpp.pop("mwrap_onnxruntime_config_detail")
    text = "// Generated from the official 1.25.1 public API AST.\nexport {\n"
    text += "".join(f"using ::{name};\n" for name in capi) + "}\n"
    for namespace, names in cpp.items():
        text += f"export namespace {namespace} {{\n"
        text += "".join(f"using ::{namespace}::{name};\n" for name in names) + "}\n"
    config_text = "// Generated from the official SDK configuration key headers.\n"
    config_text += "".join(f"export inline const char* const {name} = mwrap_onnxruntime_config_detail::{name};\n"
                           for name in sorted(config_keys))
    outputs = {root / "src/exports.inc": text,
               root / "src/config_exports.inc": config_text,
               root / "upstream/api-surface.json": json.dumps(
                   {"version": "1.25.1", "c": capi, "cpp": cpp["Ort"],
                    "config-keys": sorted(config_keys),
                    "cpp-namespaces": {name: names for name, names in cpp.items() if name != "Ort"}}, indent=2) + "\n"}
    for path, content in outputs.items():
        if args.check:
            if path.read_text() != content:
                raise SystemExit(f"API surface differs: regenerate {path.relative_to(root)}")
        else:
            path.write_text(content)
    print(f"Exported {len(capi)} C declarations/enumerators and {sum(map(len, cpp.values()))} C++ declarations")
