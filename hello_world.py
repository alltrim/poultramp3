import time

def main():
    while True:
        print("Hello, world at ", time.strftime('%Y.%m.%d %H:%M:%S'))
        time.sleep(0.1)

if __name__ == "__main__":
    main()

