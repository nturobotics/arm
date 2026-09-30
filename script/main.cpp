#include <AccelStepper.h>
#include <Servo.h>

// --- CNC Shield V3 引腳定義 ---
#define X_STEP 2
#define X_DIR  5
#define Y_STEP 3
#define Y_DIR  6
#define Z_STEP 4
#define Z_DIR  7
#define ENABLE 8     // CNC Shield 全域致能腳
#define SERVO_PIN 11 // 通常接在 Shield 上的 Z+ 或 Endstop 位置

// --- 機械參數設定 ---
// 假設驅動器調在 1/16 細分，馬達一圈 200 步，則 200 * 16 = 3200 步/圈
const float stepsPerDegree = 3200.0 / 360.0; 

// 初始化馬達物件 (1 代表使用外部驅動器)
AccelStepper stepperX(1, X_STEP, X_DIR);
AccelStepper stepperY(1, Y_STEP, Y_DIR);
AccelStepper stepperZ(1, Z_STEP, Z_DIR);
Servo gripper;

void setup() {
  Serial.begin(115200);
  
  // 啟動 CNC Shield 馬達驅動
  pinMode(ENABLE, OUTPUT);
  digitalWrite(ENABLE, LOW); 

  // --- 方向翻轉修正 ---
  // 翻轉大臂(Y)與二臂(Z)的邏輯方向
  // 參數：invertDirection, invertStep, invertEnable
  stepperX.setPinsInverted(false, false, false);
  stepperY.setPinsInverted(true, false, false); 
  stepperZ.setPinsInverted(true, false, false);

  // 設定最大速度與加速度 (可根據穩定度調整)
  stepperX.setMaxSpeed(2000); stepperX.setAcceleration(1000);
  stepperY.setMaxSpeed(1500); stepperY.setAcceleration(800);
  stepperZ.setMaxSpeed(2000); stepperZ.setAcceleration(1000);

  // 夾爪初始化
  gripper.attach(SERVO_PIN);
  gripper.write(90); // 預設中間位置
}

void loop() {
  // 1. 接收來自 Python 的指令
  if (Serial.available() > 0) {
    // 格式範例: "45.0,90.0,30.0,120\n"
    String data = Serial.readStringUntil('\n');
    int c1 = data.indexOf(',');
    int c2 = data.indexOf(',', c1 + 1);
    int c3 = data.indexOf(',', c2 + 1);

    if (c1 != -1 && c2 != -1 && c3 != -1) {
      float tx = data.substring(0, c1).toFloat();
      float ty = data.substring(c1 + 1, c2).toFloat();
      float tz = data.substring(c2 + 1, c3).toFloat();
      int ts = data.substring(c3 + 1).toInt();

      // 計算目標步數並移動
      stepperX.moveTo(tx * stepsPerDegree);
      stepperY.moveTo(ty * stepsPerDegree);
      stepperZ.moveTo(tz * stepsPerDegree);
      gripper.write(ts);
    }
  }

  // 2. 驅動馬達運轉 (非阻塞式)
  stepperX.run();
  stepperY.run();
  stepperZ.run();

  // 3. 定期回傳目前角度給 Python (數位分身同步用)
  static unsigned long lastUpdate = 0;
  if (millis() - lastUpdate > 100) {
    Serial.print(stepperX.currentPosition() / stepsPerDegree, 1); Serial.print(",");
    Serial.print(stepperY.currentPosition() / stepsPerDegree, 1); Serial.print(",");
    Serial.print(stepperZ.currentPosition() / stepsPerDegree, 1); Serial.print(",");
    Serial.println(gripper.read());
    lastUpdate = millis();
  }
}
