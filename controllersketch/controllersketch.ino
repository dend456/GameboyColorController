const byte BUTTON_LEFT = 12;
const byte BUTTON_DOWN = 11;
const byte BUTTON_SELECT = 10;
const byte BUTTON_RIGHT = 9;
const byte BUTTON_UP = 8;
const byte BUTTON_B = 7;
const byte BUTTON_A = 6;
const byte BUTTON_START = 5;

const byte BUTTON_LEFT_BIT  = 0b00000001;
const byte BUTTON_DOWN_BIT  = 0b00000010;
const byte BUTTON_SELECT_BIT= 0b00000100;
const byte BUTTON_RIGHT_BIT = 0b00001000;
const byte BUTTON_UP_BIT    = 0b00010000;
const byte BUTTON_B_BIT     = 0b00100000;
const byte BUTTON_A_BIT     = 0b01000000;
const byte BUTTON_START_BIT = 0b10000000;

const byte MODE_FREEPLAY = 1;
const byte MODE_RECORD = 2;
const byte MODE_REPLAY = 3;

const byte FRAME_INT_PIN = 3;
const int BUFFER_SIZE = 512;
const byte CHANGE_MODE_BYTE = 0xFF;
const byte SEND_BYTE = 0xFF ^ BUTTON_LEFT_BIT;
const byte FINISHED_REPLAY = 0xFF ^ BUTTON_RIGHT_BIT;

volatile byte mode = MODE_FREEPLAY;
volatile byte buttons = 0;

class Buffer
{
private:
  volatile int start = 0;
  volatile int end = 0;
  volatile byte buffer[BUFFER_SIZE];
public:
  byte next()
  {
    byte b = buffer[start++];
    if(start >= BUFFER_SIZE)
    {
      start = 0;
    }
    return b;
  }

  bool hasNext()
  {
    return start != end;
  }

  void add(byte b)
  {
    buffer[end++] = b;
    if(end >= BUFFER_SIZE)
    {
      end = 0;
    }
  }

  int length()
  {
    if(start <= end)
    {
      return end - start;
    }
    return (BUFFER_SIZE - start) + end;
  }

  void clear()
  {
    start = 0;
    end = 0;
  }
};

Buffer inputBuffer;
Buffer outputBuffer;

void setup()
{
  Serial.begin(19200);

  changeMode(MODE_FREEPLAY);

  pinMode(FRAME_INT_PIN, INPUT_PULLUP);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  attachInterrupt(digitalPinToInterrupt(FRAME_INT_PIN), frameInt, FALLING);
}

void changeMode(byte newMode)
{
  for(int i=BUTTON_START; i <= BUTTON_LEFT; ++i)
  {
    pinMode(i, INPUT);
    digitalWrite(i, LOW);  
  }
  inputBuffer.clear();
  buttons = 0;
  mode = newMode;
}

void record()
{
  byte newButtons = 0;
  for(byte pin=BUTTON_START; pin <= BUTTON_LEFT; ++pin)
  {
    if(digitalRead(pin) == LOW)
    {
      newButtons |= 1 << (pin - BUTTON_START);
    }
  }

  buttons = newButtons;
  outputBuffer.add(buttons);
}

void playback()
{ 
  if(!inputBuffer.hasNext())
  {
    return;
  }
  
  buttons = inputBuffer.next();
  
  if(mode == MODE_REPLAY && buttons == FINISHED_REPLAY)
  {
    changeMode(MODE_FREEPLAY);
    outputBuffer.add(FINISHED_REPLAY);
    return;
  }
  
  for(int pin=BUTTON_LEFT; pin >= BUTTON_START; --pin, buttons >>= 1)
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

  if(mode == MODE_REPLAY)
  {
    outputBuffer.add(SEND_BYTE);
  }
}

void frameInt()
{
  if(mode == MODE_RECORD)
  {
    digitalWrite(LED_BUILTIN, HIGH);
    record();
  }
  else if(mode == MODE_REPLAY)
  {
    digitalWrite(LED_BUILTIN, LOW);
    playback();
  }
}


void loop()
{
  while(inputBuffer.length() < BUFFER_SIZE - 1 && Serial.available())
  {
    byte b = Serial.read();
    if(b == CHANGE_MODE_BYTE)
    {
      while(!Serial.available());
      b = Serial.read();
      changeMode(b);
    }
    else
    {
      inputBuffer.add(b);
    }
  }

  while(outputBuffer.hasNext())
  {
    Serial.write(outputBuffer.next());
  }

  if(mode == MODE_FREEPLAY)
  {
    playback();
  }
}
