from __future__ import annotations

import argparse
import json
import sys

from tunemeta import artwork, tagging
from tunemeta.providers import DEFAULT_PROVIDER, PROVIDERS


def _get_provider(name: str):
    try:
        return PROVIDERS[name]
    except KeyError:
        available = ", ".join(sorted(PROVIDERS))
        raise SystemExit(f"Unknown provider '{name}'. Available: {available}")


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("identifier", help="A song URL, numeric ID, or free-text search query")
    parser.add_argument(
        "--provider",
        default=DEFAULT_PROVIDER,
        choices=sorted(PROVIDERS),
        help=f"Metadata source (default: {DEFAULT_PROVIDER})",
    )


def cmd_info(args: argparse.Namespace) -> None:
    provider = _get_provider(args.provider)
    metadata = provider.lookup(args.identifier)
    payload = metadata.to_dict()
    payload["artwork_url"] = provider.artwork_url(metadata, args.art_size)
    print(json.dumps(payload, indent=2))


def cmd_art(args: argparse.Namespace) -> None:
    provider = _get_provider(args.provider)
    metadata = provider.lookup(args.identifier)
    url = provider.artwork_url(metadata, args.size)
    if not url:
        raise SystemExit("No artwork available for this track.")
    image_bytes = artwork.fetch(url)
    if args.format == "jpeg":
        image_bytes = artwork.resize_jpeg(image_bytes, args.size)
    with open(args.output, "wb") as f:
        f.write(image_bytes)
    print(f"Saved artwork to {args.output}")


def cmd_tag(args: argparse.Namespace) -> None:
    provider = _get_provider(args.provider)
    metadata = provider.lookup(args.identifier)

    artwork_jpeg = None
    if not args.no_art:
        url = provider.artwork_url(metadata, args.art_size)
        if url:
            artwork_jpeg = artwork.resize_jpeg(artwork.fetch(url), args.art_size)

    tagging.write_tags(args.file, metadata, artwork_jpeg)
    print(f"Tagged {args.file}")
    print(json.dumps(metadata.to_dict(), indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tunemeta",
        description="Look up clean ID3 metadata and cover art for a song, and write it into your MP3s.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    info_parser = subparsers.add_parser("info", help="Print cleaned-up metadata as JSON")
    _add_common_args(info_parser)
    info_parser.add_argument("--art-size", type=int, default=1000, help="Artwork edge length in px (default 1000)")
    info_parser.set_defaults(func=cmd_info)

    art_parser = subparsers.add_parser("art", help="Download cover art to a file")
    _add_common_args(art_parser)
    art_parser.add_argument("-o", "--output", required=True, help="Output file path")
    art_parser.add_argument("--size", type=int, default=1000, help="Artwork edge length in px (default 1000)")
    art_parser.add_argument(
        "--format", choices=["jpeg", "original"], default="jpeg", help="Re-encode as JPEG, or save as downloaded"
    )
    art_parser.set_defaults(func=cmd_art)

    tag_parser = subparsers.add_parser("tag", help="Write looked-up metadata into a local MP3 file")
    tag_parser.add_argument("file", help="Path to the MP3 file to tag")
    _add_common_args(tag_parser)
    tag_parser.add_argument(
        "--art-size", type=int, default=800, help="Embedded artwork edge length in px (default 800)"
    )
    tag_parser.add_argument("--no-art", action="store_true", help="Skip embedding cover art")
    tag_parser.set_defaults(func=cmd_tag)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except (LookupError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
