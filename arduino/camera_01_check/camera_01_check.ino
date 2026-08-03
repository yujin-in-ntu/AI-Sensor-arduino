/*
  카메라 1단계: OV7675 영상이 정상인지 28x28 문자 그림으로 확인합니다.
  PC의 check_camera_terminal.py가 명령을 보내고 터미널에 결과를 표시합니다.
*/
#include <Arduino_OV767X.h>

const int CAMERA_WIDTH = 160;
const int CAMERA_HEIGHT = 120;
const int IMAGE_SIZE = 28;
byte cameraFrame[CAMERA_WIDTH * CAMERA_HEIGHT];
byte digitImage[IMAGE_SIZE * IMAGE_SIZE];

void makeDigitImage() {
  Camera.readFrame(cameraFrame);

  // 160x120 영상의 중앙 120x120을 골라 28x28로 축소합니다.
  // 흰 종이(밝음)는 0, 검은 펜(어두움)은 255가 되도록 반전합니다.
  for (int y = 0; y < IMAGE_SIZE; ++y) {
    int sourceY = (y * CAMERA_HEIGHT) / IMAGE_SIZE;
    for (int x = 0; x < IMAGE_SIZE; ++x) {
      int sourceX = 20 + (x * CAMERA_HEIGHT) / IMAGE_SIZE;
      byte gray = cameraFrame[sourceY * CAMERA_WIDTH + sourceX];
      int inverted = 255 - gray;
      digitImage[y * IMAGE_SIZE + x] =
          inverted <= 60 ? 0 : ((inverted - 60) * 255) / 195;
    }
  }
}

void printAsciiImage() {
  const char levels[] = " .:-=+*#%@";
  for (int y = 0; y < IMAGE_SIZE; ++y) {
    for (int x = 0; x < IMAGE_SIZE; ++x) {
      byte pixel = digitImage[y * IMAGE_SIZE + x];
      int level = (pixel * 9) / 255;
      Serial.print(levels[level]);
    }
    Serial.println();
  }
}

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 5000) {}

  // 키트의 카메라 모델을 OV7675로 명시합니다.
  if (!Camera.begin(QQVGA, GRAYSCALE, 1, OV7675)) {
    Serial.println("오류: OV7675 카메라를 시작하지 못했습니다.");
    while (true) delay(1000);
  }
 // Camera.testPattern();
  Serial.println("카메라 준비 완료. PC 터미널 확인 프로그램을 실행하세요.");
}

void loop() {
  if (!Serial.available()) return;
  String command = Serial.readStringUntil('\n');
  command.trim();

  // Python 프로그램이 올바른 01 스케치가 실행 중인지 확인합니다.
  if (command == "PING") {
    Serial.println("HELLO,CAMERA_CHECK");
    return;
  }

  // p/P는 기존 시리얼 모니터 사용자를 위해 계속 지원합니다.
  if (command != "CAPTURE" && command != "p" && command != "P") return;

  makeDigitImage();
  Serial.println("BEGIN_ASCII,28,28");
  printAsciiImage();
  Serial.println("END_ASCII");
}
