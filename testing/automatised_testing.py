import sys
import requests
import json

URL = 'http://127.0.0.1:5000/'

TO_TEST = [
    [f"{URL}book", "POST", "testing/single_book.json", "Correct book post"],
    [f"{URL}book", "POST", "testing/wrong_id.json", "String ID book post"],
    [f"{URL}book", "POST", "testing/negative_id.json", "Negative ID book post"],
    [f"{URL}book", "PUT", "testing/edited_book.json", "Editing existing book"],
    [f"{URL}book", "PUT", "testing/nonexisting_book.json", "Editing nonexisting book"],
    [f"{URL}book?id=1", "GET", ""],
    [f"{URL}book?id=1", "DELETE", ""]
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