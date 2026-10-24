#!/usr/bin/env python3
"""Render the shipped default template with mcpp, then build and run it."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib


def run(command, cwd, env=None):
    print("+", " ".join(map(str, command)), flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, help="Candidate mcpp-index containing compat.onnxruntime")
    parser.add_argument("--mcpp", default="mcpp")
    parser.add_argument("--toolchain", default="llvm@23.1.3")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    version = tomllib.loads((root / "mcpp.toml").read_text(encoding="utf-8"))["package"]["version"]
    with tempfile.TemporaryDirectory(prefix="mwrap-ort-template-") as directory:
        temporary = Path(directory)
        home = temporary / "home"
        package = home / f"registry/data/xpkgs/mcpplibs.mwrap-x-onnxruntime/{version}/onnxruntime-{version}"
        shutil.copytree(root, package, ignore=shutil.ignore_patterns(
            ".git", "target", ".mcpp", ".xlings", "__pycache__", "mcpp.lock", "compile_commands.json", "candidate-index", "mcpp-2026.*"))
        index = home / "indices/mcpplibs/pkgs/mwrap"
        index.mkdir(parents=True)
        (index / "mcpplibs.mwrap.onnxruntime.lua").write_text('''package = {
spec="1", namespace="mcpplibs.mwrap", name="onnxruntime",
description="Local installed-package template fixture", type="package",
xpm={linux={["__WRAPPER_VERSION__"]={url="https://example.invalid/ort.tar.gz",sha256="fixture"}},
macosx={["__WRAPPER_VERSION__"]={url="https://example.invalid/ort.tar.gz",sha256="fixture"}},
windows={["__WRAPPER_VERSION__"]={url="https://example.invalid/ort.zip",sha256="fixture"}}},
mcpp="mcpp.toml"}
'''.replace('__WRAPPER_VERSION__', version))
        env = dict(os.environ, MCPP_HOME=str(home))
        run([args.mcpp, "new", "--list-templates", f"mcpplibs.mwrap.onnxruntime@{version}"], temporary, env)
        run([args.mcpp, "new", "inference-app", "--template", f"mcpplibs.mwrap.onnxruntime@{version}"], temporary, env)
        project = temporary / "inference-app"
        manifest = project / "mcpp.toml"
        parsed = tomllib.loads(manifest.read_text())
        dependency = parsed["dependencies"]["mcpplibs.mwrap.onnxruntime"]
        assert dependency == version or dependency.get("version") == version, dependency
        # Keep the rendered dependency's identity/version check above. For an
        # unpublished candidate, build that exact staged source via a local edge.
        text = manifest.read_text().replace(f'"mcpplibs.mwrap.onnxruntime" = "{version}"',
            '"mcpplibs.mwrap.onnxruntime" = { path = "' + package.as_posix() + '" }')
        if args.index:
            text += '\n[indices]\ncompat = { path = "' + args.index.resolve().as_posix() + '" }\n'
        manifest.write_text(text)
        run([args.mcpp, "run", "--toolchain", args.toolchain], project)
