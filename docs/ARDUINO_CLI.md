# Arduino CLI로 컴파일·업로드

Arduino IDE 2의 버튼 대신 터미널 명령으로 스케치를 컴파일하고 업로드하는 선택 과정입니다. 처음 배우는 학생은 IDE 2 방식부터 성공시킨 뒤 사용하는 것을 권장합니다.

## 1. Arduino CLI 설치

[Arduino CLI 공식 설치 문서](https://docs.arduino.cc/arduino-cli/installation)를 따라 설치합니다.

macOS에서 Homebrew를 사용한다면:

```bash
brew update
brew install arduino-cli
```

Windows에서는 공식 Windows MSI/실행 파일을 설치하고 `arduino-cli.exe`가 PATH에 포함되게 합니다.

확인:

```text
arduino-cli version
```

## 2. Nano 33 BLE 코어 설치

모든 운영체제에서 명령은 같습니다.

```text
arduino-cli core update-index
arduino-cli core install arduino:mbed_nano
arduino-cli core list
```

목록에 `arduino:mbed_nano`가 보여야 합니다.

Arduino 라이브러리는 운영체제별 설치 문서의 안내대로 Sketchbook의 `libraries` 폴더에 Git으로 설치합니다.

## 3. 보드와 포트 확인

```text
arduino-cli board list
```

Nano 33 BLE의 FQBN은 다음과 같습니다.

```text
arduino:mbed_nano:nano33ble
```

아래 명령의 `<PORT>`를 실제 값으로 바꿉니다.

- Windows: `COM5`
- macOS: `/dev/cu.usbmodem1101`

## 4. 01 카메라 확인 스케치

저장소 최상위 폴더에서 컴파일합니다.

```text
arduino-cli compile --fqbn arduino:mbed_nano:nano33ble arduino/camera_01_check
```

업로드:

```text
arduino-cli upload --port <PORT> --fqbn arduino:mbed_nano:nano33ble arduino/camera_01_check
```

01 업로드 후 Arduino CLI 모니터 대신 실제 카메라 확인 창을 엽니다. `<PORT>`를
실제 포트로 바꿉니다.

Windows:

```powershell
.\.venv\Scripts\python.exe python\preview_camera.py --port COM5
```

macOS:

```bash
python python/preview_camera.py --port <PORT>
```

`OV7675 원본 160x120 미리보기` 창에서 실제 영상을 확인합니다.

## 5. 02 Full View 수집 스케치

```text
arduino-cli compile --fqbn arduino:mbed_nano:nano33ble arduino/camera_02_collect
arduino-cli upload --port <PORT> --fqbn arduino:mbed_nano:nano33ble arduino/camera_02_collect
```

이 단계에서는 `arduino-cli monitor`를 실행하지 않습니다. Python 미리보기 또는 수집 GUI가 포트를 사용해야 합니다.

## 6. 모델 학습

먼저 [공통 실습 문서](EXPERIMENT.md)에 따라 데이터를 수집하고 모델을 학습합니다. 다음 파일이 생성되어야 합니다.

```text
arduino/camera_03_inference/model_data.h
```

파일이 없으면 `03`은 자리표시자만 포함하므로 추론할 수 없습니다.

## 7. 03 추론 스케치

```text
arduino-cli compile --fqbn arduino:mbed_nano:nano33ble arduino/camera_03_inference
arduino-cli upload --port <PORT> --fqbn arduino:mbed_nano:nano33ble arduino/camera_03_inference
```

업로드 후 Python 추론 GUI를 실행합니다.

Windows:

```powershell
.\.venv\Scripts\python.exe python\run_inference_gui.py --port COM5
```

macOS:

```bash
python python/run_inference_gui.py --port <PORT>
```

## 8. 업로드 포트가 갑자기 바뀔 때

Nano 보드가 부트로더 모드로 들어가면 포트 이름이 잠시 바뀔 수 있습니다.

1. 보드의 RESET 버튼을 빠르게 두 번 누릅니다.
2. `arduino-cli board list`를 다시 실행합니다.
3. 새 포트로 업로드합니다.

## 9. 예상되는 경고

다음 문구는 마지막 컴파일 결과가 성공이면 치명적 오류가 아닙니다.

```text
Arduino_OV767X ... mbed ... mbed_nano ... 호환되지 않을 수 있습니다
Precompiled library ... not found
```

`fatal error`, `Compilation error`, `Error during build`가 나오면 [오류 해결 문서](TROUBLESHOOTING.md)를 확인하세요.
