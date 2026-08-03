/*
  실제 03 추론 코드의 학생용 복사본입니다.
  완성본에서 실제로 실행되는 양자화, 역양자화, Softmax, 최댓값 선택 문장
  8개만 빈칸으로 두었습니다. 빈칸을 채워 업로드하면 학생이 작성한 문장이
  보드의 실제 카메라 추론에 사용되고 run_inference_gui.py와 그대로 연결됩니다.
*/
#include <Arduino_OV767X.h>
#include <math.h>
#include <TensorFlowLite.h>
#include "tensorflow/lite/c/common.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/micro/system_setup.h"
#include "tensorflow/lite/schema/schema_generated.h"

#if __has_include("model_data.h")
  #include "model_data.h"
#else
  #include "model_data_placeholder.h"
#endif

const int CAMERA_WIDTH = 160;
const int CAMERA_HEIGHT = 120;
const int IMAGE_SIZE = 28;
const int INK_THRESHOLD = 50;
const int MNIST_DIGIT_SIZE = 20;
const int CURVED_DIGIT_RATIO_PERCENT = 16;
const int CURVED_DIGIT_MIN_WIDTH = 16;
const float UNKNOWN_THRESHOLD = 0.55f;

byte cameraFrame[CAMERA_WIDTH * CAMERA_HEIGHT];
byte digitImage[IMAGE_SIZE * IMAGE_SIZE];
// 160x120개의 참/거짓 값을 비트로 저장해 RAM 사용량을 19.2KB에서 2.4KB로 줄입니다.
byte inkMask[(CAMERA_WIDTH * CAMERA_HEIGHT + 7) / 8];

constexpr int TENSOR_ARENA_SIZE = 110 * 1024;
alignas(16) uint8_t tensorArena[TENSOR_ARENA_SIZE];

const tflite::Model* model = nullptr;
tflite::MicroMutableOpResolver<4> resolver;
tflite::MicroInterpreter* interpreter = nullptr;
TfLiteTensor* inputTensor = nullptr;
TfLiteTensor* outputTensor = nullptr;
bool modelReady = false;

void setInkPixel(int index, bool value) {
  byte bit = 1 << (index & 7);
  if (value) {
    inkMask[index >> 3] |= bit;
  } else {
    inkMask[index >> 3] &= ~bit;
  }
}

bool getInkPixel(int index) {
  return (inkMask[index >> 3] & (1 << (index & 7))) != 0;
}

bool findLongestRun(bool mask[], int length, int& bestStart, int& bestEnd) {
  bestStart = -1;
  bestEnd = -1;
  int start = -1;
  for (int i = 0; i <= length; ++i) {
    bool value = i < length ? mask[i] : false;
    if (value && start < 0) {
      start = i;
    } else if (!value && start >= 0) {
      if (bestStart < 0 || i - start > bestEnd - bestStart + 1) {
        bestStart = start;
        bestEnd = i - 1;
      }
      start = -1;
    }
  }
  return bestStart >= 0;
}

void bridgeSmallGaps(bool mask[], int length, int maxGap) {
  int index = 0;
  while (index < length) {
    if (mask[index]) {
      ++index;
      continue;
    }
    int start = index;
    while (index < length && !mask[index]) ++index;
    if (start > 0 && index < length && index - start <= maxGap) {
      for (int i = start; i < index; ++i) mask[i] = true;
    }
  }
}

void makeDigitImage() {
  Camera.readFrame(cameraFrame);

  // 1) 세로 방향으로 밝은 픽셀이 많이 이어지는 가장 큰 종이 영역을 찾습니다.
  bool goodColumns[CAMERA_WIDTH];
  for (int x = 0; x < CAMERA_WIDTH; ++x) {
    int brightCount = 0;
    for (int y = 0; y < CAMERA_HEIGHT; ++y) {
      if (cameraFrame[y * CAMERA_WIDTH + x] > 100) ++brightCount;
    }
    goodColumns[x] = brightCount >= (CAMERA_HEIGHT * 35) / 100;
  }
  bridgeSmallGaps(goodColumns, CAMERA_WIDTH, 12);

  int left, right;
  if (!findLongestRun(goodColumns, CAMERA_WIDTH, left, right) ||
      right - left + 1 < 20) {
    left = 20;
    right = 139;
  }

  // 2) 찾은 종이 열 안에서 가로 방향의 종이 범위도 찾습니다.
  bool goodRows[CAMERA_HEIGHT];
  int paperWidth = right - left + 1;
  for (int y = 0; y < CAMERA_HEIGHT; ++y) {
    int brightCount = 0;
    for (int x = left; x <= right; ++x) {
      if (cameraFrame[y * CAMERA_WIDTH + x] > 100) ++brightCount;
    }
    goodRows[y] = brightCount >= (paperWidth * 35) / 100;
  }
  bridgeSmallGaps(goodRows, CAMERA_HEIGHT, 12);

  int top, bottom;
  if (!findLongestRun(goodRows, CAMERA_HEIGHT, top, bottom) ||
      bottom - top + 1 < 20) {
    top = 0;
    bottom = CAMERA_HEIGHT - 1;
  }

  // 3) 자동 노출에 맞춰 종이 자체의 평균 밝기를 구합니다.
  long paperSum = 0;
  long paperCount = 0;
  for (int y = top; y <= bottom; ++y) {
    for (int x = left; x <= right; ++x) {
      int gray = cameraFrame[y * CAMERA_WIDTH + x];
      if (gray > 100) {
        paperSum += gray;
        ++paperCount;
      }
    }
  }
  int paperLevel = paperCount > 0 ? paperSum / paperCount : 200;

  // 4) 종이 가장자리와 검은 책상이 들어오지 않도록 종이 안쪽 8%만 검사합니다.
  int marginX = max(3, ((right - left + 1) * 8) / 100);
  int marginY = max(3, ((bottom - top + 1) * 8) / 100);
  int innerLeft = left + marginX;
  int innerRight = right - marginX;
  int innerTop = top + marginY;
  int innerBottom = bottom - marginY;
  memset(inkMask, 0, sizeof(inkMask));
  memset(digitImage, 0, sizeof(digitImage));
  if (innerLeft >= innerRight || innerTop >= innerBottom) return;

  int innerWidth = innerRight - innerLeft + 1;
  for (int y = innerTop; y <= innerBottom; ++y) {
    int inkCount = 0;
    for (int x = innerLeft; x <= innerRight; ++x) {
      bool isInk = paperLevel - cameraFrame[y * CAMERA_WIDTH + x] > INK_THRESHOLD;
      setInkPixel(y * CAMERA_WIDTH + x, isInk);
      if (isInk) ++inkCount;
    }
    // 공책의 가로줄처럼 종이를 길게 가로지르는 선은 숫자에서 제외합니다.
    if (inkCount * 100 >= innerWidth * 55) {
      for (int x = innerLeft; x <= innerRight; ++x) {
        setInkPixel(y * CAMERA_WIDTH + x, false);
      }
    }
  }

  // 5) 실제 숫자 획이 이어지는 열과 행을 찾아 숫자만 자릅니다.
  bool digitColumns[CAMERA_WIDTH];
  for (int x = 0; x < CAMERA_WIDTH; ++x) digitColumns[x] = false;
  for (int x = innerLeft; x <= innerRight; ++x) {
    int count = 0;
    for (int y = innerTop; y <= innerBottom; ++y) {
      count += getInkPixel(y * CAMERA_WIDTH + x) ? 1 : 0;
    }
    digitColumns[x] = count >= 2;
  }
  bridgeSmallGaps(digitColumns, CAMERA_WIDTH, 3);

  int digitLeft, digitRight;
  if (!findLongestRun(digitColumns, CAMERA_WIDTH, digitLeft, digitRight)) return;

  bool digitRows[CAMERA_HEIGHT];
  for (int y = 0; y < CAMERA_HEIGHT; ++y) digitRows[y] = false;
  for (int y = innerTop; y <= innerBottom; ++y) {
    for (int x = digitLeft; x <= digitRight; ++x) {
      if (getInkPixel(y * CAMERA_WIDTH + x)) {
        digitRows[y] = true;
        break;
      }
    }
  }
  bridgeSmallGaps(digitRows, CAMERA_HEIGHT, 3);

  int digitTop, digitBottom;
  if (!findLongestRun(digitRows, CAMERA_HEIGHT, digitTop, digitBottom)) return;

  // 6) 비율을 유지해 긴 쪽을 20픽셀로 줄이고 MNIST처럼 28x28 중앙에 놓습니다.
  int sourceWidth = digitRight - digitLeft + 1;
  int sourceHeight = digitBottom - digitTop + 1;
  int targetWidth;
  int targetHeight;
  if (sourceWidth >= sourceHeight) {
    targetWidth = MNIST_DIGIT_SIZE;
    targetHeight = max(1, (sourceHeight * MNIST_DIGIT_SIZE + sourceWidth / 2) / sourceWidth);
  } else {
    targetHeight = MNIST_DIGIT_SIZE;
    targetWidth = max(1, (sourceWidth * MNIST_DIGIT_SIZE + sourceHeight / 2) / sourceHeight);
  }
  bool widenAfterCleanup =
      sourceWidth * 100 >= sourceHeight * CURVED_DIGIT_RATIO_PERCENT &&
      targetWidth < CURVED_DIGIT_MIN_WIDTH;
  int offsetX = (IMAGE_SIZE - targetWidth) / 2;
  int offsetY = (IMAGE_SIZE - targetHeight) / 2;

  for (int y = 0; y < targetHeight; ++y) {
    int sourceY0 = digitTop + (y * sourceHeight) / targetHeight;
    int sourceY1 = digitTop + ((y + 1) * sourceHeight) / targetHeight;
    if (sourceY1 <= sourceY0) sourceY1 = sourceY0 + 1;
    for (int x = 0; x < targetWidth; ++x) {
      int sourceX0 = digitLeft + (x * sourceWidth) / targetWidth;
      int sourceX1 = digitLeft + ((x + 1) * sourceWidth) / targetWidth;
      if (sourceX1 <= sourceX0) sourceX1 = sourceX0 + 1;

      int gray = 255;
      for (int sourceY = sourceY0; sourceY < sourceY1; ++sourceY) {
        for (int sourceX = sourceX0; sourceX < sourceX1; ++sourceX) {
          int candidate = cameraFrame[sourceY * CAMERA_WIDTH + sourceX];
          if (candidate < gray) gray = candidate;
        }
      }
      int darkness = paperLevel - gray;
      int value = darkness <= INK_THRESHOLD
                    ? 0
                    : ((darkness - INK_THRESHOLD) * 255) / 150;
      if (value > 255) value = 255;
      digitImage[(offsetY + y) * IMAGE_SIZE + offsetX + x] = value;
    }
  }

  // 회색 원본이 아니라 배경과 획을 정리한 결과만 넓혀 획 사이가 붙지 않게 합니다.
  if (widenAfterCleanup) {
    byte narrowDigit[IMAGE_SIZE * IMAGE_SIZE];
    memcpy(narrowDigit, digitImage, sizeof(narrowDigit));
    memset(digitImage, 0, sizeof(digitImage));
    int wideOffsetX = (IMAGE_SIZE - CURVED_DIGIT_MIN_WIDTH) / 2;
    for (int y = 0; y < targetHeight; ++y) {
      for (int x = 0; x < CURVED_DIGIT_MIN_WIDTH; ++x) {
        int position256 = targetWidth > 1
                            ? (x * (targetWidth - 1) * 256) /
                              (CURVED_DIGIT_MIN_WIDTH - 1)
                            : 0;
        int x0 = position256 / 256;
        int x1 = min(x0 + 1, targetWidth - 1);
        int weight = position256 & 255;
        int value0 = narrowDigit[(offsetY + y) * IMAGE_SIZE + offsetX + x0];
        int value1 = narrowDigit[(offsetY + y) * IMAGE_SIZE + offsetX + x1];
        int value = (value0 * (256 - weight) + value1 * weight) / 256;
        digitImage[(offsetY + y) * IMAGE_SIZE + wideOffsetX + x] = value;
      }
    }
  }
}

bool prepareInput() {
  if (!inputTensor || inputTensor->type != kTfLiteInt8 ||
      inputTensor->bytes != IMAGE_SIZE * IMAGE_SIZE) {
    Serial.println("오류: 모델 입력은 28x28 INT8이어야 합니다.");
    return false;
  }

  float scale = inputTensor->params.scale;
  int zeroPoint = inputTensor->params.zero_point;
  for (int i = 0; i < IMAGE_SIZE * IMAGE_SIZE; ++i) {
    // TODO ARD1: 실제 입력 픽셀을 0~1 실수로 정규화합니다.
    // 힌트: 정수 나눗셈을 피하려면 255.0f처럼 실수를 사용합니다.
    float normalized = ____ARD1____;

    // TODO ARD2: 정규화한 값을 모델 입력 INT8 좌표로 양자화합니다.
    // 힌트: normalized / scale을 roundf()로 반올림한 뒤 zeroPoint를 더합니다.
    int value = ____ARD2____;
    if (value < -128) value = -128;
    if (value > 127) value = 127;
    inputTensor->data.int8[i] = (int8_t)value;
  }
  return true;
}

void sendPrediction(bool guiMode) {
  float logits[10];
  float maxLogit = -1.0e30f;
  for (unsigned int i = 0; i < g_class_count; ++i) {
    // TODO ARD3: 실제 INT8 모델 출력을 다시 실수 logit으로 역양자화합니다.
    // 힌트: (INT8값 - zeroPoint) * scale 순서입니다.
    logits[i] = ____ARD3____;
    if (logits[i] > maxLogit) maxLogit = logits[i];
  }

  float probabilities[10];
  float total = 0;
  for (unsigned int i = 0; i < g_class_count; ++i) {
    // TODO ARD4: 실제 Softmax 분자를 계산합니다.
    // 힌트: 값이 너무 커지지 않도록 expf(logits[i] - maxLogit)을 사용합니다.
    probabilities[i] = ____ARD4____;
    total += probabilities[i];
  }

  int bestIndex = 0;
  float bestProbability = 0;
  for (unsigned int i = 0; i < g_class_count; ++i) {
    // TODO ARD5: 모든 클래스 확률의 합이 1이 되게 만듭니다.
    probabilities[i] ____ARD5____;

    // TODO ARD6~ARD8: 실제 예측 숫자가 될 가장 큰 확률의 위치를 찾습니다.
    // 힌트: 비교에는 >, 값 저장에는 = 를 사용합니다.
    if (____ARD6____) {
      ____ARD7____;
      ____ARD8____;
    }
  }

  if (guiMode) {
    // PC GUI에는 원본 화면과 한 줄짜리 예측 결과를 전송합니다.
    Serial.print("FRAME,");
    Serial.println(CAMERA_WIDTH * CAMERA_HEIGHT);
    Serial.write(cameraFrame, CAMERA_WIDTH * CAMERA_HEIGHT);
    Serial.println();

    Serial.print("RESULT,");
    Serial.print(g_class_labels[bestIndex]);
    Serial.print(',');
    Serial.print(bestProbability, 6);
    Serial.print(',');
    Serial.print(g_class_count);
    for (unsigned int i = 0; i < g_class_count; ++i) {
      Serial.print(',');
      Serial.print(g_class_labels[i]);
      Serial.print(',');
      Serial.print(probabilities[i], 6);
    }
    Serial.println();
    return;
  }

  for (unsigned int i = 0; i < g_class_count; ++i) {
    Serial.print(g_class_labels[i]); Serial.print(": ");
    Serial.print(probabilities[i] * 100.0f, 1); Serial.println("%");
  }

  if (bestProbability < UNKNOWN_THRESHOLD) {
    Serial.print("결과: 모르겠음 (최고 후보 ");
    Serial.print(g_class_labels[bestIndex]); Serial.print(")");
  } else {
    Serial.print("예측 숫자: "); Serial.print(g_class_labels[bestIndex]);
  }
  Serial.print(", 신뢰도: ");
  Serial.print(bestProbability * 100.0f, 1);
  Serial.println("%");
}

void setupModel() {
#if MODEL_DATA_GENERATED
  // 현재 Arduino_TensorFlowLite 예제와 같은 방식으로 실행 환경을 초기화합니다.
  tflite::InitializeTarget();
  model = tflite::GetModel(g_model);
  if (model->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("오류: TFLite 모델 스키마 버전이 다릅니다.");
    return;
  }

  if (resolver.AddConv2D() != kTfLiteOk ||
      resolver.AddMaxPool2D() != kTfLiteOk ||
      resolver.AddReshape() != kTfLiteOk ||
      resolver.AddFullyConnected() != kTfLiteOk) {
    Serial.println("오류: 모델 연산 등록 실패");
    return;
  }

  static tflite::MicroInterpreter staticInterpreter(
      model, resolver, tensorArena, TENSOR_ARENA_SIZE);
  interpreter = &staticInterpreter;
  if (interpreter->AllocateTensors() != kTfLiteOk) {
    Serial.println("오류: 텐서 메모리 할당 실패");
    return;
  }

  inputTensor = interpreter->input(0);
  outputTensor = interpreter->output(0);
  if (g_class_count > 10 || outputTensor->type != kTfLiteInt8 ||
      outputTensor->bytes != g_class_count) {
    Serial.println("오류: 모델 출력 수와 클래스 수가 다릅니다.");
    return;
  }
  modelReady = true;
#else
  Serial.println("모델이 없습니다. python/train_camera_model.py를 먼저 실행하세요.");
#endif
}

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 5000) {}
  Serial.setTimeout(100);

  if (!Camera.begin(QQVGA, GRAYSCALE, 1, OV7675)) {
    Serial.println("오류: OV7675 카메라 시작 실패");
    while (true) delay(1000);
  }
  setupModel();
  if (modelReady) Serial.println("준비 완료. 숫자를 중앙에 놓고 p를 입력하세요.");
}

void loop() {
  if (!Serial.available()) return;
  String command = Serial.readStringUntil('\n');
  command.trim();

  if (command == "PING") {
    Serial.print("HELLO,INFERENCE,");
    Serial.println(modelReady ? 1 : 0);
    return;
  }
  if (!modelReady) return;

  bool guiMode = command == "PREDICT";
  bool monitorMode = command == "p" || command == "P";
  if (!guiMode && !monitorMode) return;

  makeDigitImage();
  if (!prepareInput()) return;
  if (interpreter->Invoke() != kTfLiteOk) {
    Serial.println("오류: 추론 실패");
    return;
  }
  sendPrediction(guiMode);
  if (!guiMode) Serial.println("다시 촬영하려면 p를 입력하세요.");
}
