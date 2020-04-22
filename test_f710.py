# -*- coding: utf-8 -*-
import time
import numpy as np
import donkeycar as dk

class PrintJoy:
    """
    ジョイスティックデバイス入力値を表示するテスト用パーツクラス。
    """
    def run(self, angle, throttle, mode, rec):
        """
        引数で与えられた値を表示する。
        引数：
            angle       ステアリング値
            throttle    スロットル値
            mode        運転モード
            rec         記録モード
        戻り値：
            なし
        """
        print(f'angle:{angle} throttle:{throttle} mode:{mode}, rec:{rec}')

def test_joy(cfg):
    """
    Windows PCに接続したF710操作が求めている振る舞いを行っているか
    を確認する。
    引数：
        cfg         config.py/myconfig.py オブジェクト
    戻り値：
        なし
    """
    V = dk.vehicle.Vehicle()

    V.mem['cam/image_array'] = np.zeros((120, 160,3))

    from parts.controller import get_js_controller
    ctr = get_js_controller(cfg, debug=True)
    V.add(ctr, 
        inputs=['cam/image_array'],
        outputs=['user/angle', 'user/throttle', 'user/mode', 'recording'],
        threaded=True)
    
    # ジョイスティック操作を表示するパーツ
    V.add(PrintJoy(), inputs=['user/angle', 'user/throttle', 'user/mode', 'recording'])

    try:
        print('start')
        V.start(rate_hz=cfg.DRIVE_LOOP_HZ, 
            max_loop_count=cfg.MAX_LOOPS)
    except KeyboardInterrupt:
        print('halt')
    finally:
        print('stop')


def test_joy3(cfg):
    import pygame
    #from pygame import *
    print('import pygame')
    try:
        pygame.init()
        print('pygame init')
        done = False
        while not done:
            print('loop start')
            for event in pygame.event.get():
                print(f'{event} {event.type}')
                if event.type == pygame.QUIT:
                    #if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    print('escape')
                    done = True
                    raise KeyboardInterrupt
            print('wait 1sec')
            time.sleep(1)
    except:
        raise

if __name__ == '__main__':
    """
    test_joyメソッドを実行する。
    """
    cfg = dk.load_config()
    setattr(cfg, 'CONTROLLER_TYPE', 'F710_pygame')
    test_joy(cfg)
    