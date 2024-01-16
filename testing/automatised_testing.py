import sys
import requests
import json

URL = 'http://127.0.0.1:5000/books/'
BOOK = 'book'

TO_TEST = [
    [f"{URL}{BOOK}", "POST", "testing/single_book.json", "Correct book post"],
    [f"{URL}{BOOK}", "POST", "testing/wrong_id.json", "String ID book post"],
    [f"{URL}{BOOK}", "POST", "testing/negative_id.json", "Negative ID book post"],
    [f"{URL}{BOOK}", "PUT", "testing/edited_book.json", "Editing existing book"],
    [f"{URL}{BOOK}", "PUT", "testing/nonexisting_book.json", "Editing nonexisting book"],
    [f"{URL}{BOOK}?id=1", "GET", None, "Getting book with ID 1"],
    [f"{URL}{BOOK}?id=1", "DELETE", None, "Deleting book with ID 1"]
]

def main():
    for test in TO_TEST:
        print("Starting test: " + test[-1])
        if test[2] is None:
            try:
                response = getattr(requests, test[1].lower())(test[0], data="")
                print(response.text)
            except Exception as e:
                print(str(e))
        else:
            try:
                data = {}
                with open(test[2], 'r') as file:
                    data = json.load(file)
                response = getattr(requests, test[1].lower())(test[0], json=data)
                print(response.text)
            except Exception as e:
                print(str(e))

if __name__ == '__main__':
    main()