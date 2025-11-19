"""Command-line interface for microlens-utils."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from microlens_utils.converters import converter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="microlens-utils",
        description="Convert microlensing parameters between supported packages.",
    )
    parser.add_argument("--source", required=True, help="Input package name.")
    parser.add_argument("--observer", default="earth", help="Frame observer.")
    parser.add_argument("--target", help="Destination package (optional).")
    parser.add_argument("--origin", help="Frame origin for dump().")
    parser.add_argument(
        "--input",
        required=True,
        metavar="PATH",
        help="Path to JSON file containing the source parameters.",
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        help="Path to write the converted JSON payload (stdout if omitted).",
    )
    parser.add_argument(
        "--epochs",
        nargs="*",
        type=float,
        help="Optional list of epochs to attach to the canonical model.",
    )
    return parser


def load_params(path: Path) -> Any:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise SystemExit("Input payload must be a JSON object.")
    return data


def dump_payload(path: Path | None, payload: Any) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True, default=str)
    if path:
        path.write_text(text + "\n")
    else:
        print(text)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    params = load_params(input_path)

    conv = converter(
        source=args.source,
        params=params,
        observer=args.observer,
        epochs=args.epochs,
    )

    if args.target:
        payload = conv.dump(
            args.target,
            observer=args.observer,
            origin=args.origin,
        )
    else:
        payload = {
            "scalars": dict(conv.model.scalars),
            "meta": dict(conv.model.meta),
        }

    dump_payload(Path(args.output) if args.output else None, payload)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
