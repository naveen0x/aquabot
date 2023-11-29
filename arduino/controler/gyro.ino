#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

void setup() {
  Serial.begin(9600);

  while (!Serial) {
    // Wait for serial connection
  }

  Serial.println("Initializing I2C devices...");
  mpu.initialize();

  Serial.println("Testing MPU6050 connections...");
  Serial.println(mpu.testConnection() ? "MPU6050 connection successful" : "MPU6050 connection failed");

  Serial.println("Calibrating gyro... Please make sure the MPU-6050 is stationary.");

  mpu.calibrateGyro();

  Serial.println("Gyro calibration complete. Starting program.");
  delay(1000);
}

void loop() {
  // Read raw accelerometer and gyro data
  int16_t ax, ay, az, gx, gy, gz;
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  // Display raw data
  Serial.print("Accel: ");
  Serial.print(ax); Serial.print(", ");
  Serial.print(ay); Serial.print(", ");
  Serial.print(az); Serial.print(" | ");

  Serial.print("Gyro: ");
  Serial.print(gx); Serial.print(", ");
  Serial.print(gy); Serial.print(", ");
  Serial.println(gz);

  delay(1000); // Adjust delay as needed
}
