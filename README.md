# Windows PCマシンにジョイスティックを接続してDonkey Simulator上で運転する

Donkey Simulator を操作する際、PCのキーボードもしくはWebコントローラから行う
こととなりますが、本リポジトリのdonkeycar アプリケーション(ドキュメントでは`mycar`ディレクトリ)を
使用することで、ジョイスティックによる操作が可能となります。

[![Donkey Sim with F710 Joystick](https://img.youtube.com/vi/4EWGBzdmPWs/0.jpg)](https://www.youtube.com/watch?v=4EWGBzdmPWs)

## 前提

* donkeycar パッケージのバージョンはv3.1.2とする
* pygame パッケージはv1.9.7とする
* ジョイスティックは、Logicool Wireless GamePad F710 (XInputモード)とする

> Elecom社製 JC-U4113 ワイヤレスジョイパッド(XInputモード)での動作も確認しました。F710と同じ設定で動作します。

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

### F710機能割当

* X-Dスイッチ(本体上部)は常にX側に設定すること(DirectInputモードでは動作しない)
* MODEボタン横のLEDは消灯状態に設定すること(右アナログ上下左右と十字キーの割当機能が入れ替わる)

|操作対象|割当機能|備考|
|:------|:---|:---|
|左アナログスティック左右|ステアリング操作||
|左アナログスティック上下|~~スロットル操作~~割当機能なし||
|左アナログスティック押込|スロットルおよびステアリングをゼロに|シミュレータは慣性が強いので停止しない|
|右アナログスティック左右|~~ステアリング操作~~割当機能なし||
|右アナログスティック上下|スロットル操作||
|右アナログスティック押込|スロットルおよびステアリングをゼロに|シミュレータは慣性が強いので停止しない|
|Xボタン押下|割当機能なし||
|Yボタン押下|直近の記録済みTubデータ100件削除|クラッシュ時などに使用|
|Aボタン押下|緊急停止||
|Bボタン押下|割当機能なし||
|Logicoolロゴ押下|機能なし|PCとのベアリング(?)|
|BACKボタン押下|自動一定速度速走ON/OFF|最初はOFF、押下するごとにON、OFFと入れ替わる|
|STARTボタン押下|運転モード変更|デフォルトは手動、謳歌するごとにステアリングのみ自動、完全自動、手動と入れ替わる|
|MODEボタン押下|機割当能なし(右アナログと十字キーを入れ替える)|本表はLED点灯なし状態での機能を記述|
|VIBRATIONボタン押下|割当機能なし|押すとブルブル震える|
|十字キー上押下|最大スロットル時の上限を増やす|押し込むごとに少しづつ増える|
|十字キー下押下|最大スロットル時の上限を減らす|押し込むごとに少しづつ減る|
|十字キー左押下|割当機能なし||
|十字キー右押下|割当機能なし||
|LBボタン押下|カオスモンキーON||
|LBボタン離脱|カオスモンキーOFF||
|RBボタン押下|カオスモンキーON||
|RBボタン離脱|カオスモンキーOFF||
|LTキー押下|スロットルおよびステアリングをゼロに|シミュレータは慣性が強いので停止しない|
|RTキー押下|スロットルおよびステアリングをゼロに|シミュレータは慣性が強いので停止しない|

## 終了

Ctrl+Cキーを2回押下する

## 参考

### F710 以外のジョイスティックを使用したい場合

F710設定のままで、Elecom社製 JC-U4113 ワイヤレスジョイパッド(XInputモード)での動作を確認しています。おそらくXInput互換ゲームパッドはF710設定のままでも動作する可能性があります。

動作しない場合やXInput非互換の場合は、ボタンやアナログジョイスティック、十字キー定義や機能割当を個別に修正した `parts/controller.py` を作成する必要があります。

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

## ライセンス

[MITライセンス](./LICENSE) 準拠とします。
