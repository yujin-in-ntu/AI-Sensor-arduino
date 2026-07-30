/*
  카메라 2단계: 160x120 흑백 원본을 PC로 보내 미리보고 데이터를 수집합니다.
  Python preview_camera.py 또는 collect_camera_data.py와 함께 사용합니다.
*/
#include <Arduino_OV767X.h>

const int WIDTH = 160;
const int HEIGHT = 120;
const int FRAME_BYTES = WIDTH * HEIGHT;
byte frameBuffer[FRAME_BYTES];

void setup() {
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

  if (command == "PING") {
    Serial.println("HELLO,OV7675_FULL");
    return;
  }
  if (command != "FRAME") {
    Serial.println("ERROR,BAD_COMMAND");
    return;
  }

  Camera.readFrame(frameBuffer);
  Serial.print("FRAME,");
  Serial.println(FRAME_BYTES);
  Serial.write(frameBuffer, FRAME_BYTES);
  Serial.println();
  Serial.println("END_FRAME");
}
