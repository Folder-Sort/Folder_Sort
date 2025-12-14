#include <iostream>
using namespace std;

struct Node
{
  int data;
  Node *next;

  Node(int d) : data(d), next(nullptr) {}
};

class LinkedList
{
private:
  Node *head;

public:
  LinkedList() : head(nullptr) {}

  void append(Node *n)
  {

    if (!head)
    {
      head = n;
      return;
    }

    Node *temp = head;

    while (temp->next)
      temp = temp->next;

    temp->next = n;
  }

  void insert(Node *n, int index)
  {
    if (index < 0)
    {
      cerr << "Invalid index\n";
      return;
    }

    if (index == 0)
    {
      n->next = head;
      head = n;
      return;
    }

    Node *temp = head;

    for (int i = 0; temp && i < index - 1; i++)
    {
      temp = temp->next;
    }

    if (!temp)
    {
      cerr << "Index out of range\n";
      return;
    }

    n->next = temp->next;
    temp->next = n;
  }

  void print() const
  {
    Node *temp = head;
    while (temp)
    {
      cout << temp->data << " -> ";
      temp = temp->next;
    }
    cout << "NULL\n";
  }

  ~LinkedList()
  {
    Node *curr = head;
    while (curr->next)
    {
      Node *next = curr->next;
      delete curr;
      curr = next;
    }
  }
};