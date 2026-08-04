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

bool runInference(bool guiMode) {
  if (!inputTensor || inputTensor->type != kTfLiteInt8 ||
      inputTensor->bytes != IMAGE_SIZE * IMAGE_SIZE) {
    Serial.println("오류: 모델 입력은 28x28 INT8이어야 합니다.");
    return false;
  }

  float scale = inputTensor->params.scale;
  int zeroPoint = inputTensor->params.zero_point;
  for (int i = 0; i < IMAGE_SIZE * IMAGE_SIZE; ++i) {
    // ARD1:
    // normalized 변수에는 입력 픽셀을 0~1 범위로 정규화한 값이 들어가야 합니다.
    // digitImage[i]는 현재 입력 픽셀이며 0~255의 숫자로 이루어져 있습니다.
    // digitImage[i]를 이용해 정규화 수식을 작성하세요.
    float normalized = ____ARD1____;

    // ARD2:
    // value 변수에는 normalized를 모델 입력용 INT8 좌표로 바꾼 값이 들어가야 합니다.
    // scale은 INT8 한 칸의 실수 간격이고 zeroPoint는 실수 0의 INT8 위치입니다.
    // normalized, scale, zeroPoint와 반올림 함수 roundf()를 이용해 수식을 작성하세요.
    int value = ____ARD2____;
    if (value < -128) value = -128;
    if (value > 127) value = 127;
    inputTensor->data.int8[i] = (int8_t)value;
  }

  // 위에서 채운 inputTensor를 모델에 넣어 실제 CNN 추론을 실행합니다.
  // Invoke()가 끝나면 숫자별 INT8 점수가 outputTensor에 저장됩니다.
  if (interpreter->Invoke() != kTfLiteOk) {
    Serial.println("오류: 추론 실패");
    return false;
  }

  // 이제 outputTensor의 숫자별 점수를 읽어 logit과 확률로 바꿉니다.
  float logits[10];
  float maxLogit = -1.0e30f;
  for (unsigned int i = 0; i < g_class_count; ++i) {
    // ARD3:
    // logits[i]에는 모델의 INT8 출력을 다시 실수 점수로 바꾼 값이 들어가야 합니다.
    // outputTensor->data.int8[i]는 현재 INT8 출력값입니다.
    // 출력의 zero_point와 scale을 함께 이용해 역양자화 수식을 작성하세요.
    // outputTensor->data.int8[i]: 숫자 클래스 i에 대해 모델이 출력한 양자화된 INT8 점수입니다.
    // outputTensor->params.zero_point: 실제 값 0을 INT8 좌표에서 나타내는 기준 위치입니다.
    // outputTensor->params.scale: INT8 값이 한 칸 변할 때 실제 점수가 변하는 간격입니다.
    logits[i] = ____ARD3____;
    if (logits[i] > maxLogit) maxLogit = logits[i];
  }

  float probabilities[10];
  float total = 0;
  for (unsigned int i = 0; i < g_class_count; ++i) {
    // ARD4:
    // probabilities[i]에는 현재 logit의 Softmax 분자가 들어가야 합니다.
    // expf()는 지수함수이고 maxLogit은 지수값이 너무 커지는 것을 막는 기준값입니다.
    // logits[i], maxLogit과 expf()를 이용해 수식을 작성하세요.
    probabilities[i] = ____ARD4____;
    total += probabilities[i];
  }

  int bestIndex = 0;
  float bestProbability = 0;
  for (unsigned int i = 0; i < g_class_count; ++i) {
    // ARD5:
    // total에는 모든 Softmax 분자를 더한 값이 들어 있습니다.
    // probabilities[i]가 0~1 범위의 실제 확률이 되도록 현재 값과 total로 수식을 작성하세요.
    probabilities[i] = ____ARD5____;

    // ARD6:
    // 현재 probabilities[i]가 지금까지의 bestProbability보다 클 때만 실행해야 합니다.
    // 두 변수를 비교하는 if 조건식을 작성하세요.
    if (____ARD6____) {
      // ARD7:
      // bestProbability에는 지금까지 발견한 가장 큰 확률을 저장합니다.
      // 현재 확률 probabilities[i]를 이용해 대입문의 오른쪽을 작성하세요.
      bestProbability = ____ARD7____;

      // ARD8:
      // bestIndex에는 가장 큰 확률이 발견된 클래스 위치를 저장합니다.
      // 현재 반복 위치 i를 이용해 대입문의 오른쪽을 작성하세요.
      bestIndex = ____ARD8____;
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
    return true;
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
  return true;
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
  if (!runInference(guiMode)) return;
  if (!guiMode) Serial.println("다시 촬영하려면 p를 입력하세요.");
}
