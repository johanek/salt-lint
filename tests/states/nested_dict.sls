testcase:
  file:
    - managed
    - source: salt://some/path
    - mode: '0644'
    - user: root
    - group: root
    - context:
      a: 1
      b: 2
    - defaults:
      c: 3
      d: 4
