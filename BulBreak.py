"""게임 실행 진입점."""
from pico2d import *
from codes.main import main


if __name__ == '__main__':
    open_canvas(800, 600)
    try:
        main()
    finally:
        close_canvas()
