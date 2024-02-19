NOTES
=====

### types

```
def sum_numbers(a: int, b: int) -> int:
    return a + b
```

```
name: str = 'Joe'
age: int = 32
rating: float = 6.9
is_premium: bool = True

from typing import List, Dict
names: List[str] = ['Bob','Joe']
emails: Dict[str, str] = {
    'Bob': 'bob@email.com',
    'Mark': 'mark@email.com',
    'Jack': 'jack@email.com'
}
```
### enumerate

```
for index, item in enumerate(str_items):
  print(f"{index} {item}")
```

### sort
```
items = {'a': 1, 'b': 2, 'c': 3}
sorted_items = sorted(items, lambda kv: kv[0])
```

### static method

```
class Test:
  @staticmethod
  def test_static(p1, p2):
    return p1 + p2

if __name__ == '__main__':
  print(Test.test_static(1,2))
```

### argparse

```
import argparse
parser = argparse.ArgumentParser(description='List the content of a folder')
parser.add_argument('path',
                    metavar='path',
                    type=str,
                    help='the path to list')
parser.add_argument('-l',
                    '--long',
                    action='store_true',
                    help='enable the long listing format')

args = parser.parse_args()
print(args)
```