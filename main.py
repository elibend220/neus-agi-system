import argparse
import logging
from core.core_manager import CoreManager
from agents.agent_v2_5 import AgentV2_5
from agents.agent_v3_0 import AgentV3_0

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    parser = argparse.ArgumentParser(description="NEUS AGI System")
    parser.add_argument("--mode", type=str, default="interactive", help="v2.5, v3.0, or interactive")
    parser.add_argument("--interval", type=int, default=60)
    parser.add_argument("--real", action="store_true")
    args = parser.parse_args()

    core = CoreManager(use_real_ai=args.real)

    if args.mode == "v2.5":
        agent = AgentV2_5(core=core)
        agent.run(interval=args.interval)
    elif args.mode == "v3.0":
        agent = AgentV3_0(core=core)
        agent.run(interval=args.interval)
    else:
        while True:
            print("Options:\n1) Run v2.5\n2) Run v3.0\n3) View Memory\n4) Exit")
            choice = input("Option: ")
            if choice == "1":
                agent = AgentV2_5(core=core)
                agent.run(interval=args.interval)
            elif choice == "2":
                agent = AgentV3_0(core=core)
                agent.run(interval=args.interval)
            elif choice == "3":
                print(core.memory.get_all())
            elif choice == "4":
                break

if __name__ == "__main__":
    main()
