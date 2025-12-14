#include <iostream>
#include <vector>
#include <stack>
using namespace std;

int main()
{
  vector<int> v;
  v.push_back(5);
  v.push_back(10);
  v.pop_back();
  for (int i = 0; i < v.size(); i++)
  {
    cout << v[i];
  }
  cout << endl;

  stack<string> s;
  s.push("Python");
  s.push("C++");
  s.push("JavaScript");
  s.push("TypeScript");

  for (int i = 0; i < s.size() + i; i++)
  {
    cout << s.top() << " ";
    s.pop();
  }
  return 0;
}