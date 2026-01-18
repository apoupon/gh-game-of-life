"""Command-line interface for GitHub Game of Life.

Provides CLI command for generating Game of Life GIFs from GitHub contribution data.
"""

import sys

from gh_game_of_life.core.game import BoundaryStrategy

from .config import load_config, merge_configs, validate_config
from .generate import generate_gif


def parse_args(args: list[str] | None = None) -> dict:
    """Parse command-line arguments.

    Args:
        args: List of command-line arguments. If None, uses sys.argv[1:].

    Returns:
        Dictionary with parsed arguments.

    Raises:
        SystemExit: If arguments are invalid.
        ValueError: If argument values are invalid.
    """
    if args is None:
        args = sys.argv[1:]

    parsed = {
        "config": None,
        "username": None,
        "output": None,
        "frames": None,
        "strategy": None,
        "cell_size": None,
        "frame_delay": None,
    }

    i = 0
    while i < len(args):
        arg = args[i]

        if arg in ["-h", "--help"]:
            print_help()
            sys.exit(0)

        elif arg in ["-v", "--version"]:
            print("gh-game-of-life 0.1.0")
            sys.exit(0)

        elif arg in ["--config"]:
            if i + 1 >= len(args):
                print("Error: --config requires a value", file=sys.stderr)
                sys.exit(2)
            parsed["config"] = args[i + 1]
            i += 2

        elif arg in ["-u", "--username"]:
            if i + 1 >= len(args):
                print("Error: --username requires a value", file=sys.stderr)
                sys.exit(2)
            parsed["username"] = args[i + 1]
            i += 2

        elif arg in ["-o", "--output"]:
            if i + 1 >= len(args):
                print("Error: --output requires a value", file=sys.stderr)
                sys.exit(2)
            parsed["output"] = args[i + 1]
            i += 2

        elif arg in ["-f", "--frames"]:
            if i + 1 >= len(args):
                print("Error: --frames requires a value", file=sys.stderr)
                sys.exit(2)
            try:
                parsed["frames"] = int(args[i + 1])
            except ValueError:
                print(
                    f"Error: frames must be an integer, got '{args[i + 1]}'",
                    file=sys.stderr,
                )
                sys.exit(2)
            i += 2

        elif arg in ["-s", "--strategy"]:
            if i + 1 >= len(args):
                print("Error: --strategy requires a value", file=sys.stderr)
                sys.exit(2)
            strategy_value = args[i + 1].lower()
            if strategy_value not in ["loop", "void"]:
                print(
                    f"Error: strategy must be 'loop' or 'void', got '{strategy_value}'",
                    file=sys.stderr,
                )
                sys.exit(2)
            parsed["strategy"] = strategy_value
            i += 2

        elif arg in ["-c", "--cell-size"]:
            if i + 1 >= len(args):
                print("Error: --cell-size requires a value", file=sys.stderr)
                sys.exit(2)
            try:
                parsed["cell_size"] = int(args[i + 1])
            except ValueError:
                print(
                    f"Error: cell-size must be an integer, got '{args[i + 1]}'",
                    file=sys.stderr,
                )
                sys.exit(2)
            i += 2

        elif arg in ["-d", "--frame-delay"]:
            if i + 1 >= len(args):
                print("Error: --frame-delay requires a value", file=sys.stderr)
                sys.exit(2)
            try:
                parsed["frame_delay"] = int(args[i + 1])
            except ValueError:
                print(
                    f"Error: frame-delay must be an integer, got '{args[i + 1]}'",
                    file=sys.stderr,
                )
                sys.exit(2)
            i += 2

        else:
            # Positional argument (username)
            if parsed["username"] is None:
                parsed["username"] = arg
            # Ignore additional positional arguments
            i += 1

    return parsed


def print_help() -> None:
    """Print help message."""
    help_text = """\
usage: gh-game-of-life [options] USERNAME

Transform your GitHub contribution graph into Conway's Game of Life.

Positional Arguments:
  USERNAME              GitHub username to fetch contributions for

Optional Arguments:
  -h, --help            Show this help message and exit
  -v, --version         Show version and exit
  --config FILE         Load configuration from YAML file
  -u, --username USER   GitHub username (alternative to positional)
  -o, --output PATH     Output GIF file path (default: username-gh-life.gif)
  -f, --frames N        Number of simulation frames (default: 50)
  -s, --strategy STRAT  Boundary strategy: 'loop' or 'void' (default: loop)
  -c, --cell-size PX    Pixel size per cell (default: 10)
  -d, --frame-delay MS  Milliseconds per frame (default: 500)

Configuration File (YAML):
  The --config flag can point to a YAML file with default settings.
  CLI arguments override configuration file values.

  Example config.yaml:
    username: torvalds
    frames: 100
    strategy: loop
    cell-size: 15
    output: output.gif

Examples:
  gh-game-of-life torvalds
  gh-game-of-life --config config.yaml
  gh-game-of-life --config config.yaml -f 200 -u override-user
  gh-game-of-life torvalds --strategy void --cell-size 15
"""
    print(help_text)


def main(args: list[str] | None = None) -> int:
    """Main CLI entry point.

    Args:
        args: Command-line arguments. If None, uses sys.argv[1:].

    Returns:
        Exit code (0 on success, non-zero on failure).
    """
    try:
        parsed = parse_args(args)

        # Load configuration file if specified
        file_config = {}
        if parsed["config"]:
            try:
                file_config = load_config(parsed["config"])
                file_config = validate_config(file_config)
            except FileNotFoundError as e:
                print(f"Error: {e}", file=sys.stderr)
                return 1
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                return 1
            except IOError as e:
                print(f"Error: {e}", file=sys.stderr)
                return 1

        # Prepare CLI config (only non-None values)
        cli_config = {
            k: v for k, v in parsed.items() if k != "config" and v is not None
        }

        # Merge configurations (CLI overrides file)
        merged_config = merge_configs(file_config, cli_config)

        # Apply defaults
        if "frames" not in merged_config or merged_config["frames"] is None:
            merged_config["frames"] = 50
        if "strategy" not in merged_config or merged_config["strategy"] is None:
            merged_config["strategy"] = "loop"
        if "cell_size" not in merged_config or merged_config["cell_size"] is None:
            merged_config["cell_size"] = 10
        if "frame_delay" not in merged_config or merged_config["frame_delay"] is None:
            merged_config["frame_delay"] = 500

        # Validate required arguments
        if merged_config.get("username") is None:
            print("Error: USERNAME is required", file=sys.stderr)
            print("Run 'gh-game-of-life --help' for usage information", file=sys.stderr)
            return 2

        # Determine output path
        output_path = merged_config.get("output")
        if output_path is None:
            output_path = f"{merged_config['username']}-gh-life.gif"

        # Map strategy string to enum
        strategy_map = {
            "loop": BoundaryStrategy.LOOP,
            "void": BoundaryStrategy.VOID,
        }
        strategy = strategy_map[merged_config["strategy"]]

        # Generate the GIF
        print(
            f"Generating GIF for user '{merged_config['username']}'...", file=sys.stderr
        )
        result_path = generate_gif(
            username=merged_config["username"],
            output_path=output_path,
            frames=merged_config["frames"],
            boundary_strategy=strategy,
            cell_size=merged_config["cell_size"],
            frame_delay_ms=merged_config["frame_delay"],
        )

        print(f"Success! GIF saved to: {result_path}", file=sys.stderr)
        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except IOError as e:
        print(f"Error: Failed to generate GIF: {e}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
