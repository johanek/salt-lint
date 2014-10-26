ntp:
  file:
    - managed
    - name: /etc/ntp.conf
    - source: salt://ntp/files/etc/ntp.conf
    - user: root
    - group: root
    - mode: '0644'
    - require_in:
      - service: ntp
  pkg.installed:
    - name: ntp
    - watch_in:
      - service: ntp
  service:
    - running
    - enable: True
    - require:
      - pkg: ntp
    - watch:
      - file: ntp
