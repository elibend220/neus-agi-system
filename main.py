"""Entry point for the neus-agi-system scaffold."""

from core import neus_system


def main():
    print("Starting neus-agi-system (scaffold)...")
    system = neus_system.NeusSystem()
    system.start()


if __name__ == "__main__":
    main()
