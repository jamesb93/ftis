from jinja2 import Environment, BaseLoader

_colour_tracks = """
<REAPER_PROJECT 0.1 "6.11/x64" 1591355987
  
  {%- for name, items in tracks.items() %}
  <TRACK 
    NAME "{{name}}"
    {%- for item in items %}  
    <ITEM 
      POSITION  {{item.position}}
      NAME {{item.name}}
      LENGTH {{item.length}}
      COLOR {{item.color}}
      SOFFS {{item.start}}
      <SOURCE WAVE
        FILE "{{item.file}}"
      >
    >
  {% endfor -%}
  >
  {% endfor -%}
>
"""

def render_tracks(path:str, data:dict) -> None:
    template = Environment(loader=BaseLoader()).from_string(_colour_tracks)
    with open(path, "w") as f:
        f.write(template.render(tracks=data))