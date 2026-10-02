import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.router.router import process_query


def main():
    print("Welcome to CamTech Assistant CLI! Type 'exit' or 'quit' to close.")
    print("---------------------------------------------------------------")

    # Check keys
    if not os.getenv("COHERE_API_KEY") or not (
        os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY")
    ):
        print("Warning: Missing API keys in environment.")

    session_id = "cli-session-1"

    while True:
        try:
            query = input("\nYou: ")
            if query.lower().strip() in ["exit", "quit"]:
                break
            if not query.strip():
                continue

            response = process_query(query, session_id)
            print(f"\nCamTech Assistant:\n{response['response']}")

            if response.get("sources"):
                print("\n[Sources]: " + ", ".join(response["sources"]))

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
