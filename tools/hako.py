#!/usr/bin/env python3
"""Build the tutorial-pinned zenoh-c as an optional Foundation component."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path


class ConfigError(RuntimeError):
    pass


def load_manifest(path: Path) -> dict:
    result: dict = {}
    stack: list[tuple[int, dict]] = [(-1, result)]
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if ":" not in stripped or stripped.startswith("-"):
            raise ConfigError(f"{path}:{lineno}: expected key/value mapping")
        key, value = stripped.split(":", 1)
        while indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        value = value.strip()
        if not value:
            parsed: object = {}
        elif value.lower() in {"true", "false"}:
            parsed = value.lower() == "true"
        elif value.startswith(("\"", "'")) and value[-1] == value[0]:
            parsed = value[1:-1]
        else:
            try:
                parsed = int(value)
            except ValueError:
                parsed = value
        parent[key] = parsed
        if isinstance(parsed, dict):
            stack.append((indent, parsed))
    return result


def resolved_path(value: str, root: Path) -> Path:
    path = Path(value).expanduser()
    return (path if path.is_absolute() else root / path).resolve()


def run(command: list[str], cwd: Path) -> None:
    print(">", subprocess.list2cmdline(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def yaml(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, int):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def git_revision(root: Path) -> str:
    result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], text=True, capture_output=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["doctor", "configure", "build", "test", "install", "smoke"])
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--install-dir", type=Path)
    parser.add_argument("--state-dir", type=Path)
    args = parser.parse_args(argv)

    tutorial_root = Path(__file__).resolve().parents[1]
    source = tutorial_root / "zenoh-c"
    manifest = args.config.expanduser().resolve()
    cfg = load_manifest(manifest)
    if cfg.get("version") != 1:
        raise ConfigError("version must be 1")
    build_cfg = cfg.get("build", {})
    features = cfg.get("features", {})
    validation = cfg.get("validation", {})
    build_dir = resolved_path(str(build_cfg.get("dir", "build/zenoh-c")), tutorial_root)
    in_source_tree = build_cfg.get("in_source_tree") is True
    state_dir = args.state_dir.expanduser().resolve() if args.state_dir else tutorial_root / ".hako"
    install_dir = args.install_dir.expanduser().resolve() if args.install_dir else None
    unstable = features.get("unstable_api") is True
    errors: list[str] = []
    if not (source / "CMakeLists.txt").is_file():
        errors.append(f"tutorial zenoh-c submodule is missing: {source}")
    for command in ("cmake", "cargo", "rustc"):
        if not shutil.which(command):
            errors.append(f"{command} was not found on PATH")
    if not unstable:
        errors.append("features.unstable_api=true is required by the Topology Agent")

    state_dir.mkdir(parents=True, exist_ok=True)
    resolved = state_dir / "resolved-build.yaml"
    resolved.write_text(
        "\n".join(
            [
                "version: 1",
                f"manifest: {yaml(manifest)}",
                f"source: {yaml(source)}",
                "build:",
                f"  type: {yaml(build_cfg.get('type', 'Release'))}",
                f"  dir: {yaml(build_dir)}",
                f"  in_source_tree: {yaml(in_source_tree)}",
                "features:",
                f"  unstable_api: {yaml(unstable)}",
                f"  shared_memory: {yaml(features.get('shared_memory') is True)}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Resolved configuration: {resolved}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if args.command == "doctor":
        return 1 if errors else 0
    if errors:
        raise ConfigError("doctor found blocking prerequisites")

    cmake_args = [
        f"-DCMAKE_BUILD_TYPE={build_cfg.get('type', 'Release')}",
        "-DBUILD_SHARED_LIBS=ON",
        "-DZENOHC_BUILD_WITH_UNSTABLE_API=ON",
        f"-DZENOHC_BUILD_WITH_SHARED_MEMORY={'ON' if features.get('shared_memory') is True else 'OFF'}",
        f"-DZENOHC_BUILD_IN_SOURCE_TREE={'ON' if in_source_tree else 'OFF'}",
    ]
    if install_dir:
        cmake_args.append(f"-DCMAKE_INSTALL_PREFIX={install_dir}")
    if args.command in {"configure", "build"}:
        build_dir.mkdir(parents=True, exist_ok=True)
        run(["cmake", "-S", str(source), "-B", str(build_dir), *cmake_args], tutorial_root)
    if args.command == "build":
        command = ["cmake", "--build", str(build_dir)]
        if isinstance(build_cfg.get("parallel"), int) and build_cfg["parallel"] > 0:
            command.extend(["--parallel", str(build_cfg["parallel"])])
        run(command, tutorial_root)
    elif args.command == "test" and validation.get("tests") is True:
        run(["ctest", "--test-dir", str(build_dir), "--output-on-failure"], tutorial_root)
    elif args.command == "install":
        if install_dir is None:
            raise ConfigError("install requires --install-dir")
        run(["cmake", "--install", str(build_dir), "--prefix", str(install_dir)], tutorial_root)
        receipt_dir = install_dir / "share/hakoniwa/receipts"
        resolved_target = receipt_dir / "resolved/zenoh-c.yaml"
        resolved_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(resolved, resolved_target)
        system = {"Darwin": "macos", "Linux": "linux", "Windows": "windows"}.get(platform.system(), platform.system().lower())
        machine = platform.machine().lower()
        arch = {"x86_64": "x64", "amd64": "x64", "aarch64": "arm64"}.get(machine, machine)
        receipt = receipt_dir / "zenoh-c.yaml"
        receipt.write_text(
            "\n".join(
                [
                    "schema_version: 1",
                    "component:",
                    "  id: zenoh-c",
                    "  version: 1.10.1",
                    f"  source_revision: {yaml(git_revision(source))}",
                    "platform:",
                    f"  os: {yaml(system)}",
                    f"  architecture: {yaml(arch)}",
                    "  toolchain: cmake-rust",
                    "install:",
                    f"  prefix: {yaml(install_dir)}",
                    "capabilities:",
                    "  shared_library: true",
                    "  unstable_api: true",
                    f"  shared_memory: {yaml(features.get('shared_memory') is True)}",
                    "build_limits: {}",
                    "dependencies: {}",
                    "artifacts:",
                    "  - path: lib/cmake/zenohc/zenohcConfig.cmake",
                    "    kind: cmake-package",
                    "  - path: include/zenoh.h",
                    "    kind: header",
                    "resolved_manifest: share/hakoniwa/receipts/resolved/zenoh-c.yaml",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"Component Receipt: {receipt}")
    elif args.command == "smoke":
        if install_dir is None or not (install_dir / "lib/cmake/zenohc/zenohcConfig.cmake").is_file():
            raise ConfigError("installed zenoh-c CMake package is missing")
        print("zenoh-c smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ConfigError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode or 1)
