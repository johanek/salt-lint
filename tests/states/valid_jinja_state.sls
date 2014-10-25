{% for item in ['one', 'two', 'three'] %}
{{ item }}:
  pkg:
    - installed
{% endfor %}
