#include <string>
#include <fstream>
#include <iostream>
#include <algorithm>
#include <cmath>
using std::string;
using std::ifstream;
using std::min;
using std::cout;
using std::endl;

string s1, s2;
const string::size_type ten = 10;

int main(int argc, char* argv[])
{
  ifstream std(argv[1]);
  ifstream out(argv[2]);
  int h = 0;
  while (std && out && getline(std, s1) && getline(out, s2))
  {
    h++;
    int k = s1.length();
    while (k && s1[k - 1] == ' ') k--;
    s1 = s1.substr(0, k);
    
    k = s2.length();
    while (k && s2[k - 1] == ' ') k--;
    s2 = s2.substr(0, k);
    
    if (s1 != s2)
    {
      string::size_type k = 0;
      while (k < s1.length() && k < s2.length() && s1[k] == s2[k]) k++;
      cout << "WA on (" << h << ", " << k + 1 << ")" << endl;
      if (k == s1.length())
      {
        cout << " stand      output : ...<empty>" << endl;
        cout << " competitor output : ..." + s2.substr(k, min(ten, s2.length() - k));
        
        return 1;
      }
      if (k == s2.length())
      {
        cout << " stand      output : ..." + s1.substr(k, min(ten, s1.length() - k)) << endl;
        cout << " competitor output : ...<empty>";
        
        return 2;        
      }
      
      cout << " stand      output : ..." + s1.substr(k, min(ten, s1.length() - k)) << endl;
      cout << " competitor output : ..." + s2.substr(k, min(ten, s2.length() - k));
      
      return 3;        
    }
  }    
  
  while (std)
  {
    int k = s1.length();
    while (k && s1[k - 1] == ' ') k--;
    s1 = s1.substr(0, k);
    if (s1 != "")
    {
      cout << "stand output is longer than competitor output.";
      
      return 4;        
    }
    getline(std, s1);
  }
  while (out)
  {
    int k = s2.length();
    while (k && s2[k - 1] == ' ') k--;
    s2 = s2.substr(0, k);
    if (s2 != "")
    {
      cout << "competitor output is longer than stand output.";
      
      return 5;        
    }
    getline(out, s2);
  }  
  cout << "GET!";
  
}  
