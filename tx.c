boolean toggle1 = 1;
boolean toggle3 = 1;
unsigned char tx_word[256] = "Mobile and Vehicular Network Lab!";
short int tx_data[512];
int length;
int tx_data_pos = 0;
int checksum = 0;

void setup(){
  //get word length
  for(length = 1;tx_word[length] > 0;length++);
  //calculate checksum
  for(int i=0;i<length;i++){
    checksum = (checksum*256 + int(tx_word[i]))%255;
  }
  //write checksum byte and ending byte
  tx_word[length] = (unsigned char)(checksum);
  tx_word[length+1] = 0x00;
  length += 2;
  Serial.begin(9600);
  Serial.print(tx_word[length-2]);
  //prepare tx data
  for(int i = 0;i < length;i++){
    tx_data[i*2] = (int(tx_word[i])/16+1)*5;
    tx_data[i*2+1] = (int(tx_word[i])%16+1)*5;
  }  
  length *= 2;

  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(13, OUTPUT);
  
  cli();//stop interrupts
  
  //set timer1 
  TCCR1A = 0;// set entire TCCR1A register to 0
  TCCR1B = 0;// same for TCCR1B
  TCNT1  = 0;//initialize counter value to 0

  OCR1A = 15624;
  
  // turn on CTC mode
  TCCR1B |= (1 << WGM12);
  // Set CS12 and CS10 bits for 1024 prescaler
  TCCR1B |= (1 << CS12);// | (1 << CS10);  
  // enable timer compare interrupt
  TIMSK1 |= (1 << OCIE1A);
  
  
  //set timer3 
  TCCR3A = 0;
  TCCR3B = 0;
  TCNT3  = 0;

  OCR3A = 2097; 
  
  // turn on CTC mode
  TCCR3B |= (1 << WGM32);
  TCCR3B |= (1 << CS32);// | (1 << CS30);  
  TIMSK3 |= (1 << OCIE3A);
  
  sei();//allow interrupts
  
}//end setup

ISR(TIMER1_COMPA_vect){
  toggle1 = !toggle1;
  digitalWrite(8, toggle1);
 digitalWrite(9, LOW);
}

ISR(TIMER3_COMPA_vect){
  
  /*
  toggle3 = !toggle3;
  digitalWrite(9, toggle3);
  */
  OCR1A = tx_data[tx_data_pos]; 
  TCNT1 = 0;
  digitalWrite(9, HIGH);
  tx_data_pos = (tx_data_pos+1) % length;
}

void loop() {

}
 