// Arduino Mega örnek köprü sketch'i
// ROS2 tarafındaki arduino_serial_bridge.py düğümü
// cmd_vel -> seri komut olarak göndererek
// tekerlek hızlarını Arduino'ya iletir.

const int LEFT_PWM_PIN = 5;
const int RIGHT_PWM_PIN = 6;
const int LEFT_DIR_PIN1 = 22;
const int LEFT_DIR_PIN2 = 23;
const int RIGHT_DIR_PIN1 = 24;
const int RIGHT_DIR_PIN2 = 25;

String commandBuffer = "";

void setup() {
  Serial.begin(115200);
  pinMode(LEFT_PWM_PIN, OUTPUT);
  pinMode(RIGHT_PWM_PIN, OUTPUT);
  pinMode(LEFT_DIR_PIN1, OUTPUT);
  pinMode(LEFT_DIR_PIN2, OUTPUT);
  pinMode(RIGHT_DIR_PIN1, OUTPUT);
  pinMode(RIGHT_DIR_PIN2, OUTPUT);
  Serial.println("Arduino Mega bridge ready");
}

void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      parseCommand(commandBuffer);
      commandBuffer = "";
    } else if (c != '\r') {
      commandBuffer += c;
    }
  }
}

void parseCommand(const String &command) {
  // Beklenen format: V,<left_speed>,<right_speed>
  if (command.length() < 2) {
    return;
  }

  if (command.charAt(0) != 'V') {
    return;
  }

  int firstComma = command.indexOf(',');
  int secondComma = command.indexOf(',', firstComma + 1);
  if (firstComma < 0 || secondComma < 0) {
    return;
  }

  String leftStr = command.substring(firstComma + 1, secondComma);
  String rightStr = command.substring(secondComma + 1);

  float leftSpeed = leftStr.toFloat();
  float rightSpeed = rightStr.toFloat();

  setWheelSpeed(leftSpeed, rightSpeed);
}

void setWheelSpeed(float leftSpeed, float rightSpeed) {
  // Burada leftSpeed ve rightSpeed radyan/saniye cinsinden
  // Arduino tarafında PWM değerine veya motor sürücüsüne çevrilmelidir.
  // Örnek olarak sadece yön ayarlanıp hız mutlak değere göre PWM uygulanır.

  applyMotor(LEFT_PWM_PIN, LEFT_DIR_PIN1, LEFT_DIR_PIN2, leftSpeed);
  applyMotor(RIGHT_PWM_PIN, RIGHT_DIR_PIN1, RIGHT_DIR_PIN2, rightSpeed);
}

void applyMotor(int pwmPin, int dirPin1, int dirPin2, float speed) {
  float maxSpeed = 30.0; // bu değeri motorunuzun en yüksek güvenli hızıyla uyumlu ayarlayın
  speed = constrain(speed, -maxSpeed, maxSpeed);

  if (speed >= 0) {
    digitalWrite(dirPin1, HIGH);
    digitalWrite(dirPin2, LOW);
  } else {
    digitalWrite(dirPin1, LOW);
    digitalWrite(dirPin2, HIGH);
    speed = -speed;
  }

  int pwmValue = (int)map(constrain((long)(speed * 1000.0), 0L, (long)(maxSpeed * 1000.0)), 0, (int)(maxSpeed * 1000.0), 0, 255);
  analogWrite(pwmPin, pwmValue);
}
