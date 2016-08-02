const byte BUTTON_LEFT = 5;
const byte BUTTON_UP = 9;
const byte BUTTON_RIGHT = 8;
const byte BUTTON_DOWN = 6;
const byte BUTTON_SELECT = 7;
const byte BUTTON_START = 12;
const byte BUTTON_A = 11;
const byte BUTTON_B = 10;

bool recordMode = false;
byte buttons = 0;
byte recordSequence = 0xFF;

void setup()
{
  Serial.begin(9600);

  resetButtons();

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
}

void resetButtons()
{
  for(int i=BUTTON_START; i <= BUTTON_LEFT; ++i)
  {
    pinMode(i, INPUT);
    digitalWrite(i, LOW);  
  }
  buttons = 0;
}

void record()
{
  while(Serial.available())
  {
    byte b = Serial.read();
    if(b == recordSequence)
    {
        recordMode = false;
        resetButtons();
        return;
    }
  }

  byte newButtons = 0;
  for(byte pin=BUTTON_LEFT; pin <= BUTTON_START; ++pin)
  {
    if(digitalRead(pin) == LOW)
    {
      newButtons |= 1 << (pin - BUTTON_LEFT);
    }
  }

  if(buttons != newButtons)
  {
    buttons = newButtons;
    Serial.write(buttons);
  }
}

void playback()
{
  while(!Serial.available());
  Serial.readBytes(&buttons, 1); 

  if(buttons == recordSequence)
  {
    recordMode = true;
    resetButtons();
    return;
  }
  
  for(int pin=BUTTON_START; pin >= BUTTON_LEFT; --pin, buttons >>= 1)
  {
    if(buttons & 1)
    {
      pinMode(pin, OUTPUT);
    }
    else
    {
      pinMode(pin, INPUT);
    }
  }
}

void loop()
{
  if(recordMode)
  {
    digitalWrite(LED_BUILTIN, HIGH);
    record();
  }
  else
  {
    digitalWrite(LED_BUILTIN, LOW);
    playback();
  }
}
