# -*- coding: utf-8 -*-
"""
Windows 環境下でジョイスティック(Logitech F710 Wireless Gamepad)パーツを
使うためのモジュール。
fctlや/dev/input/js0を使用するかわりにpygameを使用する。
F710はXInputモード(X Box互換)でのみ動作する（本体上部のスイッチを"X"側にすること）。
"""
import time
import logging
try:
    import pygame
except ImportError:
    print('need pygame package')
    raise
try:
    import donkeycar as dk
except ImportError:
    print('need donkeycar packages')
    raise
from donkeycar.parts.controller import JoystickController

# CONTROLLER_TYPE 指定文字列
TYPE_F710 = 'F710_pygame'

class PyGameJoystick(object):
    """
    PyGameを使ったジョイスティック入力データ群を取得するための
    基底モジュール。具現クラスにてself.axis_names, self.button_namesを
    埋める必要がある。
    """
    def __init__(self, which_js=0,
    log_filename='PyGameJoystick.log', debug=False):
        """
        初期化処理。
        対象となるジョイスティックから入力データを読み取る準備を行う。
        引数：
            which_js        ジョイスティック番号
            log_filename    ログファイル名
            debug           デバッグフラグ（TrueにするとloggingレベルがDEBUGになる）
        戻り値：
            なし
        """
        self.debug = debug
        # ロギング
        if self.debug:
            level = logging.DEBUG
            logging.basicConfig(filename=log_filename, level=level)
        if self.debug:
            print(f'joystick log filename: {log_filename}')
        logging.debug('start __init__')

        # pygame パッケージの初期化
        try:
            if not pygame.get_init():
                pygame.init()
                logging.debug('init pygame')
        except:
            logging.error('pygame init error')
            raise

        # pygame.joystick パッケージ初期化
        if not pygame.joystick.get_init():
            pygame.joystick.init()
            logging.debug('init joysticks')
        
        # 対象ジョイスティックの初期化
        count = pygame.joystick.get_count()
        logging.debug(f'joystic count: {count}')
        if count <= 0:
            logging.error('joystick not found')
            raise Exception(f'joystick not found: {count}')
        if which_js < 0 or count <= which_js:
            logging.error(f'joystick no: {which_js} is out of range from 0 to {count}')
            raise Exception(f'joystick no: {which_js} is out of range from 0 to {count}')
        self.joystick = pygame.joystick.Joystick(which_js)
        #if self.joystick.get_init():
        self.joystick.init()
        logging.debug(f'init joystick no: {which_js}')

        # ジョイスティック情報
        logging.debug(f'joystick name: {self.joystick.get_name()}')
        logging.debug(f'axis number: {self.joystick.get_numaxes()}')
        logging.debug(f'btns number: {self.joystick.get_numbuttons()}')
        logging.debug(f'hats number: {self.joystick.get_numhats()}')

        # 入力データ格納用変数の初期化
        self.axis_states = [ 0.0 for i in range(self.joystick.get_numaxes())]
        self.button_states = [ 0 for i in range(self.joystick.get_numbuttons() + self.joystick.get_numhats() * 4)]
        self.axis_names = {}
        self.button_names = {}
        logging.debug(f'axis_states length: {len(self.axis_states)}')
        logging.debug(f'button_states length: {len(self.button_states)}')
        logging.debug('end __init__')

    def poll(self):
        """
        ポーリング処理。
        イベントを取得し、ジョイスティック入力情報に変化があったものを
        戻り値として返却する。
        引数：
            なし
        戻り値：
            button          ボタン番号群
            button_state    ボタン押下有無　ON:1 or OFF:0
            axis            アナログデバイス番号群
            axis_val        アナログデバイス入力値 [-1.0, 1.0] 群
        """
        #logging.basicConfig(filename='poll.log', level=logging.DEBUG)
        logging.debug('start poll')
        # 戻り値格納用変数
        button = None
        button_state = None
        axis = None
        axis_val = None
        try:
            import pygame
        except:
            raise
        self.joystick.init()
        logging.debug('init joystick')
        
        # 最新イベントの取得
        for event in pygame.event.get():
            logging.debug(f'{event.type} {event}')
            try:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    logging.debug('pygame quit')
                    raise KeyboardInterrupt
            except:
                raise

        # アナログデバイス入力データ群
        for i in range( self.joystick.get_numaxes() ):
            val = self.joystick.get_axis( i )
            logging.debug(f'axis no: {i} {val}')
            if self.axis_states[i] != val:
                axis = self.axis_names[i]
                axis_val = val
                self.axis_states[i] = val
                logging.info(f'axis name:{axis} value:{val}')

        # ボタン入力データ群
        for i in range( self.joystick.get_numbuttons() ):
            state = self.joystick.get_button( i )
            logging.debug(f'btn  no:{i} {state}')
            if self.button_states[i] != state:
                button = self.button_names[i]
                button_state = state
                self.button_states[i] = state
                logging.info(f'btn name:{button} state: {state}')

        # HAT(DPAD)入力データ群（ボタン上下左右として置き換え）
        for i in range( self.joystick.get_numhats() ):
            hat = self.joystick.get_hat( i )
            #print(f'hats no:{i} {hat}')
            horz, vert = hat
            iBtn = self.joystick.get_numbuttons() + (i * 4)
            states = (horz == -1, horz == 1, vert == -1, vert == 1)
            for state in states:
                state = int(state)
                if self.button_states[iBtn] != state:
                    button = self.button_names[iBtn]
                    button_state = state
                    self.button_states[iBtn] = state
                    logging.info(f'btn name:{button} state: {state}')
                iBtn += 1
        # 全入力データ群の返却
        logging.debug(f'{button} {button_state} {axis} {axis_val}')
        logging.debug('end poll')
        return button, button_state, axis, axis_val


class PyGameLogitechJoystick(PyGameJoystick):
    '''
    PyGameパッケージ前提としたLogitechジョイスティッククラス。
    ボタンやアナログデバイスの割当を定義したモジュール。
    操作系は親クラスPyGameJoystickに存在する。
    '''
    def __init__(self, which_js=0, 
    log_filename='PyGameJoystick.log', debug=False):
        """
        初期化処理。
        対象となるジョイスティックから入力データを読み取る準備を行う。
        引数：
            which_js        ジョイスティック番号
            log_filename    ログファイル名
            debug           デバッグフラグ（TrueにするとloggingレベルがDEBUGになる）
        戻り値：
            なし
        """
        super().__init__(which_js=which_js, log_filename=log_filename, debug=debug)

        self.axis_names = {
            0: 'left_stick_horz',
            1: 'left_stick_vert',
            2: 'trigger', # LT:1 RT:-1
            4: 'right_stick_horz',
            3: 'right_stick_vert',
        }

        self.button_names = {
            6: 'back', # select
            7: 'start',
            #10: 'Logitech',  # not assigned

            0: 'A', # cross
            1: 'B', # circle
            2: 'X', # square
            3: 'Y', # triangle

            4: 'LB', # L1
            5: 'RB', # R1

            8: 'left_stick_press',
            9: 'right_stick_press',

            10: 'dpad_up', # HAT 0: (0, 1)
            11: 'dpad_down', # HAT 0: (0, -1)
            12: 'dpad_left', # HAT 0: (-1, 0)
            13: 'dpad_right', # HAT 0: (1, 0)
        }

class PyGameLogitechJoystickController(JoystickController):
    '''
    Logitechジョイスティックコントローラクラス。
    Donkeycarパーツとして動作する。
    '''
    def __init__(self, poll_delay=0.0,
    throttle_scale=1.0, steering_scale=1.0, throttle_dir=-1.0,
    dev_fn='/dev/input/js0', auto_record_on_throttle=True,
    log_filename='PyGameJoystick.log', debug=False):
        """
        初期化処理。
        親クラスのコンストラクタを呼び出し、
        PyGame用Logitechジョイスティックオブジェクトを初期化し
        インスタンス変数へ格納する。
        引数：
            なし
        戻り値：
            なし
        """
        super().__init__(
            poll_delay=poll_delay,
            throttle_scale=throttle_scale,
            steering_scale=steering_scale,
            throttle_dir=throttle_dir,
            dev_fn=dev_fn,
            auto_record_on_throttle=auto_record_on_throttle)
        self.debug = debug
        self.js = PyGameLogitechJoystick(
            log_filename=log_filename,debug=self.debug)

    def init_trigger_maps(self):
        '''
        ボタン・アナログデバイスへ機能を割り当てるmap群
        を初期化する。
        引数：
            なし
        戻り値：
            なし
        '''
        # ボタン押し込み時の振る舞い
        self.button_down_trigger_map = {
            # logicoolロゴ/mode/vibrationボタンは認識できない
            'start': self.toggle_mode,
            'B': self.toggle_manual_recording,
            'Y': self.erase_last_N_records,
            'A': self.emergency_stop,
            'back': self.toggle_constant_throttle,

            'RB' : self.chaos_monkey_on_right,
            'LB' : self.chaos_monkey_on_left,

            # pygameではhatだが本モジュールでは個々のボタンとして扱う
            'dpad_up' :  self.on_dpad_up,
            'dpad_down' : self.on_dpad_down,
            'dpad_left' : self.on_dpad_left,
            'dpad_right' : self.on_dpad_right,

            # アナログスティック押し込み時
            'left_stick_press' : self.normal_stop,
            'right_stick_press' : self.normal_stop,
        }
        # ボタン離脱時の振る舞い
        self.button_up_trigger_map = {
            'RB' : self.chaos_monkey_off,
            'LB' : self.chaos_monkey_off,
        }
        # アナログデバイスに値変化が発生したときの振る舞い
        self.axis_trigger_map = {
            'left_stick_horz': self.set_steering,
            #'left_stick_vert': self.set_throttle,
            'trigger':  self.normal_stop_axis,  # LT(L2)/RT(R2)
            #'right_stick_horz': self.set_steering,
            'right_stick_vert': self.set_throttle,
        }

    def normal_stop(self):
        """
        スロットル値、アングル値をゼロにする。
        引数：
            なし
        戻り値：
            なし
        """
        self.set_steering(0.0)
        self.set_throttle(0.0)

    def normal_stop_axis(self, axis_val):
        """
        axis_val 値が0.5を超えた場合もしくは-0.5より小さい場合、
        スロットル値、アングル値をゼロにする。
        引数：
            axis_val    トリガ入力レベル
        戻り値：
            なし
        """
        if axis_val > 0.5 or axis_val < -0.5:
            self.normal_stop()

    def on_dpad_up(self):
        """
        最大スロットル値を上昇させる。
        引数：
            なし
        戻り値：
            なし
        """
        self.increase_max_throttle()

    def on_dpad_down(self):
        """
        最大スロットル値を減少させる。
        引数：
            なし
        戻り値：
            なし
        """
        self.decrease_max_throttle()

    def on_dpad_left(self):
        """
        なにも処理しない。
        引数：
            なし
        戻り値：
            なし
        """
        print("dpad left un-mapped")

    def on_dpad_right(self):
        """
        なにも処理しない。
        引数：
            なし
        戻り値：
            なし
        """
        print("dpad right un-mapped")

    def shutdown(self):
        """
        親クラスの実装を処理後、__del__メソッドを呼び出す。
        引数：
            なし
        戻り値：
            なし
        """
        super().shutdown()
        self.__del__()

    def __del__(self):
        """
        PyGameを停止する。
        本メソッドは呼び出されない場合あり。
        引数：
            なし
        戻り値：
            なし
        """
        try:
            pygame.quit()
        except:
            raise

def get_js_controller(cfg, debug=False):
    """
    donkeycar.parts.controller の get_js_controller ラップ関数。
    cfg内のCONTROLLER_TYPE値がF710_pygameである場合、pygame用
    F710ジョイスティックパーツクラスを生成・初期化し返却。
    上記以外の場合は既存のget_js_controllerメソッドを使用する。
    引数：
        cfg         config.py/myconfig.py オブジェクト
        debug       デバッグオプション
    戻り値：
        ctr         ジョイスティックコントローラオブジェクト
    例外：
        Exception   CONTROLLER_TYPE値に該当するジョイスティック
                    パーツが存在しない場合
    """
    
    controller_type = getattr(cfg, 'CONTROLLER_TYPE')
    print(controller_type)
    print(controller_type == TYPE_F710)
    if controller_type == TYPE_F710:
        print('Use PyGame Logitech Joystick F710')
        try:
            ctr = PyGameLogitechJoystickController(
                throttle_dir=cfg.JOYSTICK_THROTTLE_DIR,
                throttle_scale=cfg.JOYSTICK_MAX_THROTTLE,
                steering_scale=cfg.JOYSTICK_STEERING_SCALE,
                auto_record_on_throttle=cfg.AUTO_RECORD_ON_THROTTLE,
                debug=debug)
            ctr.set_deadzone(cfg.JOYSTICK_DEADZONE)
            return ctr
        except:
            raise
    print('Use default get_js_controller')
    # 既存のget_js_controllerメソッドを使用
    from donkeycar.parts.controller import get_js_controller as current_get
    ctr = current_get(cfg)
    if ctr is None:
        raise Exception('no controller object')
    return ctr


