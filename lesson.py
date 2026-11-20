from api import run_diagnostics


def main():
    print("Connecting to router...")
    try:
        results = run_diagnostics()
    except RuntimeError as error:
        print(error)
        return

    for command, output in results.items():
        print(f"\n--- Output for: {command} ---")
        print(output)

    print("\nDisconnected successfully.")


if __name__ == "__main__":
    main()
