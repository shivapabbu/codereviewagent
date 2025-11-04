"""
Example file for testing the code review agent.
This file intentionally has some issues for demonstration.
"""

def process_data(data):
    result = []
    for x in data:
        result.append(x*2)
    return result

def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total

class DataProcessor:
    def __init__(self, config):
        self.config = config
    
    def process(self, data):
        # Missing docstring
        if not data:
            return None
        return [x * 2 for x in data]

def main():
    data = [1, 2, 3, 4, 5]
    processor = DataProcessor({})
    result = process_data(data)
    print(result)

if __name__ == "__main__":
    main()

