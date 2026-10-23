#!/usr/bin/env python3
"""Generate export-using declarations from Clang's public SDK declaration AST."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile


def generate(ast):
    declarations = ast.get("inner", [])
    namespace_ids = {n["id"] for n in declarations
                     if n.get("kind") == "NamespaceDecl" and n.get("name") == "Ort"}
    kinds = {"CXXRecordDecl", "RecordDecl", "ClassTemplateDecl", "FunctionTemplateDecl",
             "FunctionDecl", "TypeAliasDecl", "TypeAliasTemplateDecl", "EnumDecl", "VarDecl"}
    cpp, capi = set(), set()
    for namespace in declarations:
        if namespace.get("id") not in namespace_ids:
            continue
        for node in namespace.get("inner", []):
            name = node.get("name", "")
            if node.get("kind") not in kinds or not name.isidentifier() or node.get("isImplicit"):
                continue
            # Clang also places out-of-line qualified definitions here. Their
            # semantic owner is a class/detail namespace, not the public Ort scope.
            owner = node.get("parentDeclContextId")
            if owner and owner not in namespace_ids:
                continue
            if node.get("kind") == "FunctionTemplateDecl" and any(
                    x.get("kind") == "CXXMethodDecl" for x in node.get("inner", [])):
                continue
            cpp.add(name)

    def collect_c(nodes):
        for node in nodes:
            if node.get("kind") == "LinkageSpecDecl":
                collect_c(node.get("inner", []))
                continue
            name = node.get("name", "")
            public_name = name.startswith(("Ort", "ONNX")) or name in {
                "GraphOptimizationLevel", "ExecutionMode", "ExecutionOrder", "RunAsyncCallbackFn"}
            if public_name and node.get("kind") in kinds | {"TypedefDecl"}:
                capi.add(name)
                if node.get("kind") == "EnumDecl":
                    capi.update(x["name"] for x in node.get("inner", [])
                                if x.get("kind") == "EnumConstantDecl")
    collect_c(declarations)
    return sorted(capi), sorted(cpp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sdk_include", type=Path)
    parser.add_argument("--clang", default="clang++")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="mwrap-ort-exports-") as temporary:
        directory = Path(temporary)
        probe = directory / "probe.cpp"
        probe.write_text("#include <onnxruntime_cxx_api.h>\n")
        with (directory / "ast.json").open("w") as out:
            subprocess.run([args.clang, "-std=c++23", "-I", str(args.sdk_include),
                            "-Xclang", "-ast-dump=json", "-fsyntax-only", str(probe)],
                           stdout=out, check=True)
        with (directory / "ast.json").open() as source:
            capi, cpp = generate(json.load(source))
    text = "// Generated from the official 1.25.1 public API AST.\nexport {\n"
    text += "".join(f"using ::{name};\n" for name in capi) + "}\nexport namespace Ort {\n"
    text += "".join(f"using ::Ort::{name};\n" for name in cpp) + "}\n"
    (root / "src/exports.inc").write_text(text)
    (root / "upstream/api-surface.json").write_text(json.dumps(
        {"version": "1.25.1", "c": capi, "cpp": cpp}, indent=2) + "\n")
    print(f"Exported {len(capi)} C declarations/enumerators and {len(cpp)} Ort declarations")
