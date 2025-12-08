import curses

from domain.session import Session

def main():
    session = Session()
    curses.wrapper(session.start)

if __name__ == '__main__':
    main()