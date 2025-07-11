# Movies assistant (LangGraph)

Fully working example is stored in [libs/next_gen_ui_langgraph/readme_example.py](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/libs/next_gen_ui_langgraph/readme_example.py) and you can try it right away.


## 1. Install dependencies
Install NextGen UI agent packages `next-gen-ui-agent`, `next-gen-ui-langgraph` and NextGenUI web component rendering `next_gen_ui_rhds_renderer`:

```sh
pip install -U next-gen-ui-agent next-gen-ui-langgraph next_gen_ui_rhds_renderer
```

!!! note
    It's common to create a virtual environment first in your project.
    ```sh
    python3 -m venv .venv && source .venv/bin/activate
    ```

## 2. Example code

```py
{%
    include-markdown "../../libs/next_gen_ui_langgraph/readme_example.py"
%}
```

## 3. Run example

Run example to get JSON representation of the Next Gen UI Component.

```sh
python readme_example.py
```

JSON component:

```js
{
    'component': 'video-player',
    'id': 'call_zomga3r3',
    'title': 'Toy Story Trailer',
    'video': 'https://www.youtube.com/embed/v-PjgYDrg70',
    'video_img': 'https://img.youtube.com/vi/v-PjgYDrg70/maxresdefault.jpg'
}
```

## 4. Try web component rendering

Change variable `component_system` to `rhds` and rerun. You'll get web component rendering.