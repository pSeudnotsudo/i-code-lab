from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import safe

register = template.Library()

SHAPES = {
    "rect": {
        "svg_attrs": 'style="position:absolute;top:-10px;left:-10px;width:calc(100% + 40px);height:calc(100% + 22px);"',
        "viewBox": "0 0 320 74",
        "path": "M8,5 L305,3 Q315,3 316,12 L318,63 Q318,71 309,72 L10,73 Q2,73 2,64 L3,11 Q3,5 8,5 Z",
    },
    "oval": {
        "svg_attrs": 'style="position:absolute;top:-23px;left:-20px;width:calc(100% + 60px);height:calc(100% + 50px);"',
        "viewBox": "0 0 220 80",
        "path": "M110,5 Q178,1 206,22 Q228,42 204,62 Q178,80 110,78 Q42,80 16,62 Q-8,42 16,22 Q42,1 110,5 Z",
    },
    "line": {
        "svg_attrs": 'style="position:absolute;bottom:-12px;left:0;width:100%;height:14px;"',
        "viewBox": "0 0 340 14",
        "path": "M2,8 L338,8",
    },
    "wave": {
        "svg_attrs": 'style="position:absolute;bottom:-12px;left:-2px;width:calc(100% + 4px);height:18px;"',
        "viewBox": "0 0 340 18",
        "path": "M3,12 Q85,2 170,10 Q255,18 337,10",
    },
    "circle": {
        "svg_attrs": 'style="position:absolute;top:-14px;left:-12px;width:calc(100% + 24px);height:calc(100% + 30px);"',
        "viewBox": "0 0 240 74",
        "path": "M120,5 C185,3 228,18 230,37 C232,56 188,72 120,72 C52,72 8,56 10,37 C12,18 55,3 120,5 Z",
    },
}

COLOR_CLASSES = {
    "pink": "w-pink",
    "brown": "w-brown",
    "purple": "w-purple",
    "blue": "w-blue",
    "green": "w-green",
    "orange": "w-orange",
}


STROKE_COLORS = {
    "pink": "#cc1a6a",
    "brown": "#b35a00",
    "purple": "#4a3ab5",
    "blue": "#185fa5",
    "green": "#3b6d11",
    "orange": "#f97316",
}



class HighlightNode(template.Node):
    def __init__(self, nodelist, shape, color):
        self.nodelist = nodelist
        self.shape = shape
        self.color = color

    def render(self, context):
        content = self.nodelist.render(context)

        shape_cfg = SHAPES.get(self.shape, SHAPES["rect"])
        stroke = STROKE_COLORS.get(self.color, "#4a3ab5")
        word_class = COLOR_CLASSES.get(self.color, "")

        html = f"""
        <span class="hl hl-{self.shape} {word_class}">
            {content}

            <svg {shape_cfg["svg_attrs"]}
                 viewBox="{shape_cfg["viewBox"]}"
                 aria-hidden="true"
                 focusable="false">

                <path class="sk-shape"
                      stroke="{stroke}"
                      stroke-width="3"
                      fill="none"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-dasharray="1200"
                      stroke-dashoffset="1200"
                      d="{shape_cfg["path"]}" />
            </svg>
        </span>
        """

        return mark_safe(html)


@register.tag(name="highlight")
def do_highlight(parser, token):

    bits = token.split_contents()

    kwargs = {}

    for bit in bits[1:]:

        # only process key=value pairs
        if "=" in bit:
            key, value = bit.split("=", 1)
            kwargs[key] = value.strip('"').strip("'")

    shape = kwargs.get("shape", "rect")
    color = kwargs.get("color", "orange")

    nodelist = parser.parse(("endhighlight",))
    parser.delete_first_token()

    return HighlightNode(nodelist, shape, color)