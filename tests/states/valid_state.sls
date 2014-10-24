ntp:
  file:
    - managed
    - name: /etc/ntp.conf
    - source: salt://ntp/files/etc/ntp.conf
    - user: root
    - group: root
    - mode: '0644'
  pkg.installed:
    - name: ntp
  service:
    - running
    - enable: True
