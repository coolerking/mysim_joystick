# Windows PCマシンにジョイスティックを接続してDonkey Simulator上で運転する

Donkey Simulator を操作する際、PCのキーボードもしくはWebコントローラから行う
こととなりますが、本リポジトリのdonkeycar アプリケーション(ドキュメントでは`mycar`ディレクトリ)を
使用することで、ジョイスティックによる操作が可能となります。

* [動作動画](https://youtu.be/4EWGBzdmPWs)

## 前提

* donkeycar パッケージのバージョンはv3.1.2とする
* pygame パッケージはv1.9.7とする
* ジョイスティックは、Logicool Wireless GamePad F710 とする

## インストール

* [donkeycar ドキュメント:Install Donkeycar on Windows](http://docs.donkeycar.com/guide/host_pc/setup_windows/) に従い、Windows PC上にdonkeycarパッケージを導入する

> 本リポジトリは donkeycarパッケージ v3.1.2 を前提としています

* 以下のコマンドを実行し、`pygame`パッケージをインストールする

```bash
conda activate donkey
pip install pygame
```

* [GitHub:tawnkramer/gym-donkeycar](https://github.com/tawnkramer/gym-donkeycar/releases) からWindows用Donkey Simulatorバイナリを展開し、適当なフォルダ(ここでは`C:\\Users\\user_name\\projects\\DonkeySimWin\\donkey_sim.exe`として説明)に格納する

* [donkeycar ドキュメント:Donkey Simulator](http://docs.donkeycar.com/guide/simulator/)に従い、DonkeyGymを導入する（donkey createcarは、本リポジトリで代用するため不要。

```bash
cd
mkdir projects
cd projects
git clone https://github.com/tawnkramer/gym-donkeycar
conda activate donkey
pip install -e gym-donkeycar
```

* 本リポジトリを展開する

```bash
conda activate donkey
cd
cd projects
git clone https://github.com/coolerking/mysim_joystick
cd mysim_joystick
```

* `myconfig.py`を編集する

 * （オプション）`USE_JOYSTICK_AS_DEFAULT` 行をコメントアウトして `True` に変更する

 ```python
 USE_JOYSTICK_AS_DEFAULT = True
 ```

 > 上記設定を行うと `--js` オプションを付けなくてもデフォルトでジョイスティック操作となる。

 * `CONTROLLER_TYPE` 行をコメントアウトして `'F710_pygame'` に変更する

 ```python
 CONTROLLER_TYPE='F710_pygame'
 ```

 > 本リポジトリのコードには上記のタイプのみ対応している。

 * `DONKEY_GYM` 行をコメントアウトして `True` に変更する

 ```python
 DONKEY_GYM = True
 ```

 * `DONKEY_SIM_PATH` 行をコメントアウトして `donkey_sim.exe` が存在するパスに変更する

 ```python
 DONKEY_SIM_PATH="C:\\Users\\hogehoge\\projects\\DonkeySimWin\\donkey_sim.exe"
 ```

  * （オプション）`GYM_CONF` 行をコメントアウトして表示車両をカスタマイズする（以下は例）

  ```python
  GYM_CONF={"body_style": "bare", "body_rgb": (128, 9, 100), "car_name": "kit", "font_size": 100}
  ```

  > 複数台走らせる場合は `"car_name"` は変更しておくこと。

* `manage.py` を編集する

修正前：

```python        
    from donkeycar.parts.controller import get_js_controller
    
    ctr = get_js_controller(cfg)
```

修正後：

```python
    #from donkeycar.parts.controller import get_js_controller
    from parts.controller import get_js_controller
    ctr = get_js_controller(cfg)
```

> `get_js_controller()`の引数に`debug=True`を追加すると、ログファイルを出力します

## 実行

* F710上部のボタンがX側にセットする

> Direct Inputモードには対応していません（要コード変更）

* Windows PCにF710付属のUSBドングルを接続する
* ドライバがインストールされ、F710が認識されたら、本体中央のLogicoolボタンを押す
* `donkey_sim.exe`を実行する
* 以下のコマンドを実行する

手動運転の場合：

```bash
cd
cd projects\mysim_joystick
conda activate donkey
python manage.py drive --js
```

手動・自動運転を切り替えたい場合：

```bash
cd
cd projects\mysim_joystick
conda activate donkey
python manage.py drive --js　--model models\hogehoge.h5
```

## 終了

Ctrl+Cキーを2回押下する

## 参考

### F710 以外のジョイスティックを使用したい場合

対象のジョイスティックをWindows PCへ接続し、ドライバインストールを完了させた後、以下のコマンドを実行してボタンやアナログスティック、トリガボタン、十字キーの`pygame`上でのマッピング情報を取得します。

```bash
cd
cd projects\mysim_joystick
conda activate donkey
python check_key_binding.py
```

ボタン、axis、hatの割当を確認したら、本リポジトリの`parts/controller.py`を参考に独自のマッピングをせっていしたパーツクラスを作成してください。

### 注意

pygame パッケージは、画面を用いたゲームアプリケーションを開発するための総合パッケージです。Donkey Simulatorで使用する場合は、画面はシミュレータ側のプログラムを使用するため pygame内のjoystickモジュールのみを使用することになります。

しかし、pygameパッケージを使用する際の初期化処理を実行すると、Ctrl+Cを含むキーボード割り当てはすべて`pygame.event` がフックするためpygameフレームワーク外で使用することができません。このため本リポジトリでは　Ctrl+C のイベントが発生した場合pygameを終了し `keyboardInterrupt` 例外を`raise`しています。
