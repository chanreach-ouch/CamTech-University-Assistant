import os
import sys


def main():
    keys_to_check = [
        "LLM_PROVIDER",
        "GROQ_API_KEY",
        "GEMINI_API_KEY",
        "COHERE_API_KEY",
        "DATABASE_URL",
    ]

    from dotenv import load_dotenv

    load_dotenv()

    print("Checking environment configuration...")
    print("-" * 40)

    missing = False

    for key in keys_to_check:
        val = os.getenv(key)
        if not val:
            print(f"{key}: MISSING")
            missing = True
        elif val.startswith("your-") or val.endswith("-here"):
            print(f"{key}: PLACEHOLDER")
            missing = True
        else:
            print(f"{key}: SET")

    print("-" * 40)
    if missing:
        print("WARNING: Some keys are missing or still set to placeholders.")
        sys.exit(1)
    else:
        print("SUCCESS: All configuration keys are SET.")
        sys.exit(0)


if __name__ == "__main__":
    main()
