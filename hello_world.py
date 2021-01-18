import time

def main():
    while true:
        print("Hello, world at ", time.strftime('%Y.%m.%d %H:%M:%S'))
        time.sleep(5)

if __name__ == "__main__":
    main()

