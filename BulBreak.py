"""게임 실행 진입점."""
# 이곳에 메인루프를 만들되 최대한 game_framework를 활용하여 작성할 것
# 이걸로 상태머신 표현할 것: from transitions import *
from pico2d import * # pico2d는 이걸로 불러올 것
from codes.main import main


if __name__ == '__main__':
    open_canvas(800, 600)
    try:
        hide_lattice()
        main()
    finally:
        close_canvas()
