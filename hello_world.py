import time

def log(*args, **kwargs):
    with open("hello.log", "a") as file:
        file.writelines(args)
        file.write("\r\n")


def main():
    while True:
        log("Hello, world at ", time.strftime('%Y.%m.%d %H:%M:%S'))
        time.sleep(10)

if __name__ == "__main__":
    main()

