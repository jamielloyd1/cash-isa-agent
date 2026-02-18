from agent import CashISAAgent


def main():
    agent = CashISAAgent()

    print("Cash ISA Banking Assistant")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        response = agent.chat(user_input)
        print(f"\nAssistant: {response}\n")


if __name__ == "__main__":
    main()
