import sys

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        # Remove the 'cli' argument so that argparse can parse everything cleanly
        sys.argv.pop(1)
        from port_scanner.cli import run_cli
        run_cli()
    else:
        from port_scanner.gui import run_gui
        run_gui()

if __name__ == "__main__":
    main()
