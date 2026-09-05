import argparse
import json
import sys
import zipfile
from pathlib import Path

REQUIRED_FIELDS = ("type", "name", "author", "version", "entry")


def load_manifest(manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    missing = [field for field in REQUIRED_FIELDS if not manifest.get(field)]
    if missing:
        raise ValueError(f"manifest.json missing required fields: {', '.join(missing)}")
    return manifest


def write_package(library: Path, manifest_path: Path, output: Path, icon: Path | None) -> None:
    if not library.is_file():
        raise FileNotFoundError(f"Library not found: {library}")
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    manifest = load_manifest(manifest_path)
    entry_name = library.name
    if manifest["entry"] != entry_name:
        raise ValueError(
            f"manifest.json entry '{manifest['entry']}' does not match "
            f"built library name '{entry_name}'"
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    manifest_bytes = json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.writestr("manifest.json", manifest_bytes)
        archive.write(library, entry_name)
        if icon is not None and icon.is_file():
            archive.write(icon, icon.name)

    with zipfile.ZipFile(output, "r") as archive:
        expected = {"manifest.json", entry_name}
        if icon is not None and icon.is_file():
            expected.add(icon.name)
        names = set(archive.namelist())
        if names != expected:
            raise RuntimeError(f"Unexpected package entries: {sorted(names)}")
        if archive.getinfo(entry_name).file_size != library.stat().st_size:
            raise RuntimeError("Library verification failed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--icon", required=False, type=Path, default=None)
    args = parser.parse_args()
    try:
        write_package(
            args.library.resolve(),
            args.manifest.resolve(),
            args.output.resolve(),
            args.icon.resolve() if args.icon else None,
        )
    except Exception as error:
        print(error, file=sys.stderr)
        return 1
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
