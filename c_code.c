#include <stdio.h>
#include <unistd.h>
#include <fstream>
#include <wiringPi.h>

#include "../Adafruit_ADS1015.h"

void printBits(size_t const size, void const * const ptr);

Adafruit_ADS1115 ads;

int main(int argc, char *argv[])
{
  int16_t adc0;
  double milliVolts;
  double bits2milliVoltsFactor;
  
  // The ADC input range (or gain) can be changed via the following
  // functions, but be careful never to exceed VDD +0.3V max, or to
  // exceed the upper and lower limits if you adjust the input range!
  // Setting these values incorrectly may destroy your ADC!
  //                                                                ADS1015  ADS1115
  //                                                                -------  -------
  // ads.setGain(GAIN_TWOTHIRDS);  // 2/3x gain +/- 6.144V  1 bit = 3mV      0.1875mV (default)
  // ads.setGain(GAIN_ONE);        // 1x gain   +/- 4.096V  1 bit = 2mV      0.125mV
  // ads.setGain(GAIN_TWO);        // 2x gain   +/- 2.048V  1 bit = 1mV      0.0625mV
  // ads.setGain(GAIN_FOUR);       // 4x gain   +/- 1.024V  1 bit = 0.5mV    0.03125mV
  // ads.setGain(GAIN_EIGHT);      // 8x gain   +/- 0.512V  1 bit = 0.25mV   0.015625mV
  // ads.setGain(GAIN_SIXTEEN);    // 16x gain  +/- 0.256V  1 bit = 0.125mV  0.0078125mV
  ads.setGain(GAIN_FOUR);
  bits2milliVoltsFactor = 0.03125; // remember to change this according to gain

  //FILE* fp = fopen("data.txt", "w");
  //fputc('a', fp);
  std::ofstream myfile;
  myfile.open("data.txt");
  ads.begin();
  //while (true) {
  int n = 500;
  printf("Go!\n");
  double data[n];
  // Threshold is 1000, will assert ALERT pin when exceeded
  ads.startComparator_SingleEnded(2, 1000);
  for (int i = 0; i < n; i++) {
    //adc0 = ads.readADC_Differential_2_3();
    adc0 = ads.getLastConversionResults();
    //milliVolts = adc0 * bits2milliVoltsFactor; 
    //data[i] = milliVolts;
    //myfile << milliVolts << "\n";
    //putw(n, fp);
    //fputc('\n', fp);
    //fputc(EOF, fp);
    //fputc((char)adc0, fp);
    //printBits(sizeof(adc0), &adc0);
    //printf(" *** %5d *** %f\n", adc0, milliVolts);
    //usleep(100000);
    //usleep(50000 / n);
  }
  printf("%d\n", 1000000 / n);
  printf("done\n");
  myfile.close();
/*
  fclose(fp);
  fp = fopen("data.txt", "r");
  int num = getw(fp);
  printf("%d\n", num);
*/
}

//assumes little endian
void printBits(size_t const size, void const * const ptr)
{
  unsigned char *b = (unsigned char*) ptr;
  unsigned char byte;
  int i, j;

  for (i=size-1;i>=0;i--) {
    for (j=7;j>=0;j--) {
      byte = (b[i] >> j) & 1;
      printf("%u", byte);
    }
  }
  //puts("");
}
