def print_red(text):
    print(f"\033[31m{text}\033[0m")
    raise Exception(text)

def print_orange(text):
    print(f"\033[33m{text}\033[0m")

