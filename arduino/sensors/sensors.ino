float calibration = 22.90; //change this value to calibrate
const int analogInPin = A1;
int sensorValue = 0;
unsigned long int avgValue;
float b, y;
int buf[10], temp;

#include <OneWire.h>
#include <DallasTemperature.h>
#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

#define SIGNAL_PIN A0
// Floats for ADC voltage & Input voltage
float adc_voltage = 0.0;
float in_voltage = 0.0;
// Floats for resistor values in divider (in ohms)
float R1 = 30000.0;
float R2 = 7500.0;
// Float for Reference Voltage
float ref_voltage = 5.0;
// Integer for ADC value
int adc_value = 0;


void setup() {
  Serial.begin(9600);
  sensors.begin();
}
void loop() {
  for (int i = 0; i < 10; i++)
  {
    buf[i] = analogRead(analogInPin);
    delay(1);
  }
  for (int i = 0; i < 9; i++)
  {
    for (int j = i + 1; j < 10; j++)
    {
      if (buf[i] > buf[j])
      {
        temp = buf[i];
        buf[i] = buf[j];
        buf[j] = temp;
      }
    }
  }
  
  avgValue = 0;
  for (int i = 2; i < 8; i++)
    avgValue += buf[i];
  float pHVol = (float)avgValue * 5.0 / 1024 / 6;
  float x = -5.70 * pHVol + calibration;
  ph = (1.4825 * x) - 3.5483;
  delay(500);


  adc_value = analogRead(SIGNAL_PIN);
  adc_voltage  = (adc_value * ref_voltage) / 1024.0;
  in_voltage = (adc_voltage / (R2 / (R1 + R2))) ;
  int battary = ( in_voltage / 24) * 100;

  delay(500);

  sensors.requestTemperatures();
  float temperatureCelsius = sensors.getTempCByIndex(0);
  delay(500);


  String sensorData = "{\"temp\":" + String(temperatureCelsiu) + ",\"pressure\":" + String(20.1) + ",\"ph\":" + String(ph) + ",\"battery\":" + String(battary)+"}";
  Serial.println(sensorData);
}
