/*
  카메라 1단계: OV7675의 실제 160x120 흑백 원본을 PC 확인 창으로 보냅니다.
  업로드한 뒤 Python preview_camera.py를 실행합니다.
*/
#include <Arduino_OV767X.h>

const int WIDTH = 160;
const int HEIGHT = 120;
const int FRAME_BYTES = WIDTH * HEIGHT;
byte frameBuffer[FRAME_BYTES];

void setup() {
  // 원본 19,200바이트를 빠르게 보내기 위해 921600 baud를 사용합니다.
  Serial.begin(921600);
  while (!Serial && millis() < 5000) {}
  Serial.setTimeout(100);

  if (!Camera.begin(QQVGA, GRAYSCALE, 1, OV7675)) {
    Serial.println("ERROR,CAMERA_BEGIN_FAILED");
    while (true) delay(1000);
  }
  Camera.noTestPattern();
  Serial.println("HELLO,OV7675_FULL");
}

void loop() {
  if (!Serial.available()) return;
  String command = Serial.readStringUntil('\n');
  command.trim();

  // Python 프로그램이 카메라와 올바른 스케치가 준비됐는지 확인합니다.
  if (command == "PING") {
    Serial.println("HELLO,OV7675_FULL");
    return;
  }
  if (command != "FRAME") {
    Serial.println("ERROR,BAD_COMMAND");
    return;
  }

  // 한 장을 촬영해 헤더, 원본 바이트, 종료 표시 순서로 보냅니다.
  Camera.readFrame(frameBuffer);
  Serial.print("FRAME,");
  Serial.println(FRAME_BYTES);
  Serial.write(frameBuffer, FRAME_BYTES);
  Serial.println();
  Serial.println("END_FRAME");
}
