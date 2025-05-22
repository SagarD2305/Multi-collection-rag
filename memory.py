class Memory:
    def __init__(self):
        self.history = []

    def add_interaction(self, query, response):
        """Add a user query and bot response to the history."""
        self.history.append({"query": query, "response": response})

    def get_history(self, limit=5):
        """Retrieve the most recent interactions."""
        return self.history[-limit:]

    def clear(self):
        """Clear the interaction history."""
        self.history = []

if __name__ == '__main__':
    # Example usage
    memory = Memory()
    memory.add_interaction("Hello, how are you?", "I'm doing well, thank you!")
    memory.add_interaction("What's the weather like?", "It's sunny today.")
    print(memory.get_history()) 