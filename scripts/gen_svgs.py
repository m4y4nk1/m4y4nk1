#!/usr/bin/env python3
"""Generate the self-hosted animated SVGs used by README.md.

Run:  python3 scripts/gen_svgs.py     (writes into ../assets)

Why hand-written SVG: GitHub renders README images through <img>, and its
image proxy serves SVG with the CSP
    default-src 'none'; img-src data:; style-src 'unsafe-inline'
(observed with REA on a live profile capture). So inside an SVG:
  * <script> never runs           -> animate with CSS @keyframes or SMIL
  * external fonts/images blocked -> use system font stacks, inline shapes
  * inline <style> is allowed     -> CSS animations work
Everything below is deterministic (seeded RNG) so regenerating is stable.
"""
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
GOLD = "#fdb927"
PURPLE = "#552583"
W, H = 1200, 320

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
MONO = "'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', 'Courier New', monospace"


def stars(rng, n, w, h, max_y):
    out = []
    for i in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, max_y)
        r = rng.choice([0.6, 0.8, 1.0, 1.2, 1.6])
        dur = rng.uniform(2.0, 5.5)
        delay = rng.uniform(0, 5)
        fill = GOLD if rng.random() < 0.08 else "#ffffff"
        out.append(
            f'<circle class="tw" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" '
            f'style="animation-duration:{dur:.2f}s;animation-delay:-{delay:.2f}s"/>'
        )
    return "\n    ".join(out)


def ridge(rng, w, base, amp, step, peak_x=None, peak_h=0, bottom=None, margin=80):
    """Polygon for a jagged mountain ridge, optionally with one tall summit.

    The ridge extends `margin` px past both edges so parallax sway never
    reveals a gap at the sides.
    """
    bottom = H if bottom is None else bottom
    pts, x = [], -margin
    while x <= w + margin + step:
        y = base - rng.uniform(0, amp)
        if peak_x is not None:
            d = abs(x - peak_x)
            if d < 260:
                y -= peak_h * (1 - d / 260) ** 1.6
        pts.append((x, y))
        x += rng.uniform(step * 0.6, step * 1.4)
    if peak_x is not None:  # make sure the summit point exists exactly
        pts = [p for p in pts if abs(p[0] - peak_x) > 12]
        pts.append((peak_x, base - amp * 0.3 - peak_h))
        pts.sort()
    poly = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    return f"{-margin},{bottom} {poly} {w + margin},{bottom}"


def shooting_stars():
    # (start x, start y, length, delay s, duration s)
    specs = [(1150, 20, 90, 0.0, 7), (820, 10, 70, 2.4, 9), (560, 30, 60, 4.1, 8),
             (1000, 60, 80, 5.6, 11), (380, 8, 55, 7.3, 10)]
    out = []
    for x, y, ln, delay, dur in specs:
        out.append(
            f'<g class="shoot" style="animation-delay:{delay}s;animation-duration:{dur}s">'
            f'<line x1="{x}" y1="{y}" x2="{x + ln}" y2="{y - ln * 0.45:.1f}" stroke="url(#trail)" '
            f'stroke-width="2" stroke-linecap="round"/></g>'
        )
    return "\n    ".join(out)


def aurora_paths():
    """Three same-structure cubic paths so SMIL can morph between them."""
    def p(a, b, c, d):
        return (f"M -100,{a} C 150,{b} 350,{c} 600,{a + 10} "
                f"S 950,{d} 1300,{b + 20}")
    return [p(110, 60, 150, 70), p(95, 130, 70, 120), p(120, 80, 120, 50)]


def car(x=0, y=0):
    """Tiny side-view car with a headlight beam and connectivity waves."""
    return f"""<g transform="translate({x},{y})">
        <path d="M60,-6 L170,-28 L170,16 Z" fill="url(#beam)"/>
        <path d="M2,-2 L6,-10 L18,-12 L26,-20 L44,-20 L52,-12 L60,-10 L62,-2 Z" fill="#0e0b1f" stroke="{GOLD}" stroke-width="1.2" stroke-linejoin="round"/>
        <path d="M27,-18 L43,-18 L49,-12 L21,-12 Z" fill="#2a2160"/>
        <circle cx="14" cy="-1" r="4" fill="#07060f" stroke="#9aa3c7" stroke-width="1.2"/>
        <circle cx="50" cy="-1" r="4" fill="#07060f" stroke="#9aa3c7" stroke-width="1.2"/>
        <circle cx="60" cy="-7" r="1.8" fill="#fff6d8"/>
        <circle cx="3" cy="-6" r="1.4" fill="#ff4d4d"/>
        <g fill="none" stroke="{GOLD}" stroke-width="1.6" stroke-linecap="round">
          <path class="sig s1" d="M29,-27 a6,6 0 0 1 12,0"/>
          <path class="sig s2" d="M25,-31 a10,10 0 0 1 20,0"/>
          <path class="sig s3" d="M21,-35 a14,14 0 0 1 28,0"/>
        </g>
      </g>"""


def header():
    rng = random.Random(24)  # 24, obviously
    peak_x = 905
    far = ridge(rng, W, 262, 40, 70)
    mid = ridge(rng, W, 292, 45, 55, peak_x, 175)
    near = ridge(rng, W, 312, 26, 40)
    summit_y = 292 - 45 * 0.3 - 175
    a1, a2, a3 = aurora_paths()
    rays = "\n        ".join(
        f'<line x1="{peak_x}" y1="{summit_y:.1f}" x2="{peak_x}" y2="{summit_y - (70 if i % 2 else 48):.1f}" '
        f'transform="rotate({i * 30} {peak_x} {summit_y:.1f})"/>' for i in range(12))
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-labelledby="t d">
  <title id="t">Mayank Mahajan</title>
  <desc id="d">Animated night sky with an aurora over a mountain range, a gold flag on the summit and a connected car driving below.</desc>
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#03040c"/>
      <stop offset="0.55" stop-color="#0b1026"/>
      <stop offset="1" stop-color="#241650"/>
    </linearGradient>
    <linearGradient id="goldtxt" x1="0" y1="0" x2="1" y2="0" spreadMethod="reflect">
      <stop offset="0" stop-color="#b8860b"/>
      <stop offset="0.5" stop-color="#fff1c2"/>
      <stop offset="1" stop-color="{GOLD}"/>
      <animateTransform attributeName="gradientTransform" type="translate"
        values="-1 0; 1 0; -1 0" dur="5s" repeatCount="indefinite"/>
    </linearGradient>
    <linearGradient id="aur" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#2ee6a6" stop-opacity="0"/>
      <stop offset="0.25" stop-color="#2ee6a6"/>
      <stop offset="0.55" stop-color="{PURPLE}"/>
      <stop offset="0.8" stop-color="{GOLD}"/>
      <stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
      <animateTransform attributeName="gradientTransform" type="translate"
        values="-0.15 0; 0.15 0; -0.15 0" dur="14s" repeatCount="indefinite"/>
    </linearGradient>
    <filter id="blur" x="-20%" y="-200%" width="140%" height="500%"><feGaussianBlur stdDeviation="16"/></filter>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <radialGradient id="moonglow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#fff6d8" stop-opacity="0.5"/>
      <stop offset="1" stop-color="#fff6d8" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="summitglow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{GOLD}" stop-opacity="0.75"/>
      <stop offset="0.4" stop-color="{GOLD}" stop-opacity="0.25"/>
      <stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="trail" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#fff" stop-opacity="0.95"/>
      <stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="beam" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#fff6d8" stop-opacity="0.55"/>
      <stop offset="1" stop-color="#fff6d8" stop-opacity="0"/>
    </linearGradient>
    <mask id="crescent"><rect width="{W}" height="{H}" fill="#fff"/><circle cx="1092" cy="62" r="25" fill="#000"/></mask>
    <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  </defs>
  <style>
    .tw {{ animation: twinkle ease-in-out infinite; }}
    @keyframes twinkle {{ 0%,100% {{ opacity: .2 }} 50% {{ opacity: 1 }} }}
    .shoot {{ animation: shoot 8s linear infinite; opacity: 0; }}
    @keyframes shoot {{
      0% {{ transform: translate(0,0); opacity: 0 }}
      2% {{ opacity: 1 }}
      12% {{ transform: translate(-460px,210px); opacity: 0 }}
      100% {{ transform: translate(-460px,210px); opacity: 0 }}
    }}
    .aurora {{ animation: breathe 9s ease-in-out infinite; }}
    @keyframes breathe {{ 0%,100% {{ opacity: .35 }} 50% {{ opacity: .75 }} }}
    .rise {{ animation: rise 1.4s cubic-bezier(.2,.8,.2,1) both; }}
    .rise.d2 {{ animation-delay: .35s; }}
    .rise.d3 {{ animation-delay: .7s; }}
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(16px) }} to {{ opacity: 1; transform: none }} }}
    .flag {{ transform-origin: {peak_x}px {summit_y - 27:.1f}px; animation: wave 1.6s ease-in-out infinite; }}
    @keyframes wave {{ 0%,100% {{ transform: scaleX(1) skewY(0deg) }} 50% {{ transform: scaleX(.85) skewY(-8deg) }} }}
    .pulse {{ animation: pulse 3s ease-in-out infinite; transform-origin: {peak_x}px {summit_y:.1f}px; }}
    @keyframes pulse {{ 0%,100% {{ opacity: .6; transform: scale(1) }} 50% {{ opacity: 1; transform: scale(1.35) }} }}
    .rays {{ animation: spin 40s linear infinite, raysfade 3s ease-in-out infinite; transform-origin: {peak_x}px {summit_y:.1f}px; }}
    @keyframes spin {{ to {{ transform: rotate(360deg) }} }}
    @keyframes raysfade {{ 0%,100% {{ opacity: .25 }} 50% {{ opacity: .7 }} }}
    .px1 {{ animation: sway 26s ease-in-out infinite alternate; }}
    .px2 {{ animation: sway2 26s ease-in-out infinite alternate; }}
    .px3 {{ animation: sway3 26s ease-in-out infinite alternate; }}
    @keyframes sway {{ from {{ transform: translateX(-10px) }} to {{ transform: translateX(10px) }} }}
    @keyframes sway2 {{ from {{ transform: translateX(-24px) }} to {{ transform: translateX(24px) }} }}
    @keyframes sway3 {{ from {{ transform: translateX(-48px) }} to {{ transform: translateX(48px) }} }}
    .drive {{ animation: drive 16s linear infinite; }}
    @keyframes drive {{ from {{ transform: translateX(-200px) }} to {{ transform: translateX({W + 60}px) }} }}
    .bob {{ animation: bob .5s ease-in-out infinite alternate; }}
    @keyframes bob {{ to {{ transform: translateY(-1px) }} }}
    .sig {{ opacity: 0; animation: sig 1.8s ease-out infinite; }}
    .s2 {{ animation-delay: .3s; }} .s3 {{ animation-delay: .6s; }}
    @keyframes sig {{ 0% {{ opacity: 0 }} 30% {{ opacity: 1 }} 100% {{ opacity: 0 }} }}
    .lane {{ animation: lane 1.2s linear infinite; }}
    @keyframes lane {{ to {{ stroke-dashoffset: -40 }} }}
    .uplink {{ animation: lane 1s linear infinite reverse; }}
    @media (prefers-reduced-motion: reduce) {{
      .tw, .shoot, .rise, .flag, .pulse, .rays, .px1, .px2, .px3, .drive, .bob, .sig, .lane, .uplink, .aurora {{ animation: none; }}
      .shoot {{ opacity: 0; }}
      .sig {{ opacity: 1; }}
      .drive {{ transform: translateX(980px); }}
    }}
  </style>
  <g clip-path="url(#frame)">
    <rect width="{W}" height="{H}" fill="url(#sky)"/>
    <!-- aurora: blurred thick strokes, SMIL path morph + CSS opacity breathing -->
    <g class="aurora" filter="url(#blur)" fill="none" stroke="url(#aur)" stroke-linecap="round">
      <path d="{a1}" stroke-width="46">
        <animate attributeName="d" values="{a1};{a2};{a3};{a1}" dur="18s" repeatCount="indefinite" calcMode="spline"
          keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/>
      </path>
      <path d="{a2}" stroke-width="22" opacity="0.7" transform="translate(0,40)">
        <animate attributeName="d" values="{a2};{a3};{a1};{a2}" dur="23s" repeatCount="indefinite" calcMode="spline"
          keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/>
      </path>
    </g>
    <!-- stars (CSS twinkle, staggered with negative delays) -->
    {stars(rng, 200, W, H, 230)}
    <!-- crescent moon (masked, so the cut-out is truly transparent) -->
    <circle cx="1080" cy="70" r="80" fill="url(#moonglow)"/>
    <circle cx="1080" cy="70" r="26" fill="#fff6d8" mask="url(#crescent)" filter="url(#glow)"/>
    <!-- shooting stars -->
    {shooting_stars()}
    <!-- parallax mountain layers -->
    <g class="px1"><polygon points="{far}" fill="#2a1f5c" opacity="0.9"/></g>
    <g class="px2">
      <g class="rays" stroke="{GOLD}" stroke-width="1.4" stroke-linecap="round">
        {rays}
      </g>
      <circle class="pulse" cx="{peak_x}" cy="{summit_y:.1f}" r="80" fill="url(#summitglow)"/>
      <polygon points="{mid}" fill="#150f30"/>
      <!-- snow cap -->
      <polygon points="{peak_x},{summit_y:.1f} {peak_x - 26},{summit_y + 30:.1f} {peak_x - 12},{summit_y + 24:.1f} {peak_x - 2},{summit_y + 34:.1f} {peak_x + 10},{summit_y + 24:.1f} {peak_x + 24},{summit_y + 30:.1f}" fill="#d9d4ff" opacity="0.18"/>
      <line x1="{peak_x}" y1="{summit_y:.1f}" x2="{peak_x}" y2="{summit_y - 34:.1f}" stroke="#e6e6e6" stroke-width="2"/>
      <polygon class="flag" points="{peak_x},{summit_y - 34:.1f} {peak_x + 28},{summit_y - 27:.1f} {peak_x},{summit_y - 20:.1f}" fill="{GOLD}" filter="url(#glow)"/>
    </g>
    <g class="px3"><polygon points="{near}" fill="#07060f"/></g>
    <!-- road with moving lane markers -->
    <rect x="0" y="300" width="{W}" height="20" fill="#05040b"/>
    <line class="lane" x1="0" y1="312" x2="{W}" y2="312" stroke="{GOLD}" stroke-opacity="0.55" stroke-width="1.5" stroke-dasharray="18 22"/>
    <!-- connected car: drives the road, pings the summit -->
    <g class="drive"><g class="bob">{car(0, 306)}</g></g>
    <!-- text -->
    <g font-family="{SANS}">
      <text class="rise" x="70" y="112" font-size="66" font-weight="800" fill="url(#goldtxt)" letter-spacing="1" filter="url(#glow)">Mayank Mahajan</text>
      <text class="rise d2" x="72" y="154" font-size="22" fill="#e3e6f3">Software Engineer @ Volkswagen Group <tspan fill="{GOLD}">·</tspan> Pune, India</text>
      <text class="rise d3" x="72" y="188" font-size="14" fill="{GOLD}" fill-opacity="0.85" font-family="{MONO}" letter-spacing="3">AUTOMOTIVE SOFTWARE · SDV · CONNECTED CAR</text>
    </g>
  </g>
</svg>
"""
    (OUT / "header.svg").write_text(svg)


def typing(lines, width=760, height=50, size=22, color=GOLD, hold=1.6, speed=0.06, erase=0.03, gap=0.35):
    """readme-typing-svg-style effect, self-hosted, using SMIL discrete steps.

    Each line gets a clipPath whose rect width steps one character at a time
    (type -> hold -> erase), and a cursor that follows it. Monospace system
    fonts are ~0.6em per glyph, which is what makes the clip widths line up.
    """
    cw = size * 0.6
    seg = []  # (start, end) of each line's slot
    t = 0.0
    for ln in lines:
        d = len(ln) * speed + hold + len(ln) * erase + gap
        seg.append((t, t + d))
        t += d
    total = t
    parts = []
    for i, ln in enumerate(lines):
        n = len(ln)
        x0 = (width - n * cw) / 2
        s, e = seg[i]
        # build discrete keyframes in absolute time, normalised later
        frames = [(0.0, 0.0)]
        frames.append((s, 0.0))
        for k in range(1, n + 1):
            frames.append((s + k * speed, k * cw))
        hold_end = s + n * speed + hold
        frames.append((hold_end, n * cw))
        for k in range(1, n + 1):
            frames.append((hold_end + k * erase, (n - k) * cw))
        frames.append((total, 0.0))
        # dedupe/normalise
        kt, vals = [], []
        for tt, v in frames:
            key = round(tt / total, 5)
            if kt and key <= kt[-1]:
                key = round(kt[-1] + 0.00001, 5)
            kt.append(min(key, 1.0))
            vals.append(v)
        kt[-1] = 1.0
        kts = ";".join(f"{k:.5f}" for k in kt)
        wv = ";".join(f"{v:.1f}" for v in vals)
        xv = ";".join(f"{x0 + v:.1f}" for v in vals)
        vis_kt = f"0;{s / total:.5f};{e / total:.5f};1"
        safe = ln.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        parts.append(f"""
  <clipPath id="c{i}"><rect x="{x0:.1f}" y="0" height="{height}" width="0">
    <animate attributeName="width" values="{wv}" keyTimes="{kts}" dur="{total:.2f}s" calcMode="discrete" repeatCount="indefinite"/>
  </rect></clipPath>
  <text x="{x0:.1f}" y="{height / 2 + size * 0.35:.1f}" clip-path="url(#c{i})">{safe}</text>
  <rect class="cur" y="{height / 2 - size * 0.55:.1f}" width="2.5" height="{size * 1.1:.1f}" fill="{color}" opacity="0">
    <animate attributeName="x" values="{xv}" keyTimes="{kts}" dur="{total:.2f}s" calcMode="discrete" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0;1;0;0" keyTimes="{vis_kt}" dur="{total:.2f}s" calcMode="discrete" repeatCount="indefinite"/>
  </rect>""")
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{' | '.join(lines)}">
  <style>
    text {{ font-family: {MONO}; font-size: {size}px; fill: {color}; white-space: pre; }}
    .cur {{ animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ fill-opacity: 0 }} }}
  </style>{''.join(parts)}
</svg>
"""
    (OUT / "typing.svg").write_text(svg)


def footer():
    rng = random.Random(8)
    h = 140
    far = ridge(rng, W, 120, 30, 60, bottom=h)
    near = ridge(rng, W, 140, 25, 45, bottom=h)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="100%" role="img" aria-label="Mamba Mentality. See you at the top.">
  <defs>
    <linearGradient id="fsky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0b1026" stop-opacity="0"/>
      <stop offset="1" stop-color="#1d1442"/>
    </linearGradient>
  </defs>
  <style>
    .tw {{ animation: twinkle ease-in-out infinite; }}
    @keyframes twinkle {{ 0%,100% {{ opacity: .2 }} 50% {{ opacity: 1 }} }}
    .glow {{ animation: glow 4s ease-in-out infinite; }}
    @keyframes glow {{ 0%,100% {{ opacity: .65 }} 50% {{ opacity: 1 }} }}
    @media (prefers-reduced-motion: reduce) {{ .tw, .glow {{ animation: none; }} }}
  </style>
  <rect width="{W}" height="{h}" fill="url(#fsky)"/>
  {stars(rng, 50, W, h, 70)}
  <polygon points="{far}" fill="#231a4d" opacity="0.9"/>
  <polygon points="{near}" fill="#07060f"/>
  <text class="glow" x="{W / 2}" y="52" text-anchor="middle" font-family="{SANS}" font-size="20" font-weight="700" letter-spacing="6" fill="{GOLD}">MAMBA MENTALITY</text>
  <text x="{W / 2}" y="78" text-anchor="middle" font-family="{MONO}" font-size="13" letter-spacing="2" fill="#8b93b0">see you at the top</text>
</svg>
"""
    (OUT / "footer.svg").write_text(svg)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    header()
    typing([
        "Automotive software engineer @ Volkswagen",
        "Software-defined vehicles enthusiast",
        "Connected car services, cloud to car",
        "Java | Spring | React | Angular | AWS",
        "Learn -> Adapt -> Kill",
    ])
    footer()
    print("wrote", ", ".join(p.name for p in sorted(OUT.glob("*.svg"))))
