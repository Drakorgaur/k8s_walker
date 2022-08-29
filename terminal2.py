#!/usr/bin/python3.9

if __name__ == '__main__':
    from app import KWApplication
    try:
        a = KWApplication()
        a.run()
    except KeyboardInterrupt:
        exit(0)

