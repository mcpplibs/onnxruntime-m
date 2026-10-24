#!/usr/bin/env python3
"""Test this wrapper against a candidate SDK index without editing the checkout."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def borrow_tools(home):
    """Reuse installed tool versions, but never reuse the SDK under test."""
    user_home = Path.home()
    for store in (user_home / ".mcpp/registry/data/xpkgs", user_home / ".xlings/data/xpkgs"):
        if not store.is_dir():
            continue
        for package in store.glob("xim-x-*"):
            if not package.is_dir():
                continue
            dest = home / "registry/data/xpkgs" / package.name
            dest.mkdir(parents=True, exist_ok=True)
            for version in package.iterdir():
                target = dest / version.name
                if not target.exists():
                    target.symlink_to(version.resolve(), target_is_directory=version.is_dir())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", required=True, type=Path)
    parser.add_argument("--mcpp", default="mcpp")
    parser.add_argument("--toolchain", default="llvm@23.1.3")
    parser.add_argument("--cold-sdk", action="store_true", help="use a fresh MCPP_HOME with no installed ORT SDK")
    parser.add_argument("--template", action="store_true", help="also render and run the default project template")
    parser.add_argument("--audit", action="store_true", help="verify generated exports with the LLVM SDK consumer command")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="mwrap-ort-candidate-") as directory:
        temporary = Path(directory)
        source = temporary / "source"
        shutil.copytree(root, source, ignore=shutil.ignore_patterns(
            ".git", "target", ".mcpp", ".xlings", "__pycache__", "mcpp.lock", "compile_commands.json",
            "candidate-index", "mcpp-2026.*"))
        with (source / "mcpp.toml").open("a") as manifest:
            manifest.write('\n[indices]\ncompat = { path = "' + args.index.resolve().as_posix() + '" }\n')
        env = dict(os.environ)
        if args.cold_sdk:
            home = temporary / "home"
            home.mkdir()
            borrow_tools(home)
            env["MCPP_HOME"] = str(home)
        command = [args.mcpp, "test", "--strict", "--toolchain", args.toolchain]
        print("+", " ".join(command), flush=True)
        subprocess.run(command, cwd=source, env=env, check=True)
        if args.audit:
            commands = json.loads((source / "compile_commands.json").read_text())
            found = None
            for entry in commands:
                arguments = entry["arguments"]
                if "clang" not in Path(arguments[0]).name:
                    continue
                for number, argument in enumerate(arguments):
                    include = arguments[number + 1] if argument == "-I" else argument[2:] if argument.startswith("-I") else ""
                    if include and (Path(include) / "onnxruntime_cxx_api.h").is_file():
                        found = (arguments[0], include)
                        break
                if found:
                    break
            assert found, "Cannot locate the resolved SDK include path and LLVM compiler for the export audit"
            subprocess.run([os.sys.executable, str(source / "tools/generate_exports.py"),
                            found[1], "--clang", found[0], "--check"], cwd=source, env=env, check=True)
        if args.cold_sdk:
            installed = [path for path in home.rglob("*onnxruntime*") if path.is_dir()]
            assert installed, "SDK did not install into the isolated home"
            print("Verified: SDK installed in the isolated home", flush=True)
        if args.template:
            subprocess.run([os.sys.executable, str(source / "tools/test_template.py"),
                            "--index", str(args.index.resolve()), "--mcpp", args.mcpp,
                            "--toolchain", args.toolchain], cwd=source, env=env, check=True)


if __name__ == "__main__":
    main()
