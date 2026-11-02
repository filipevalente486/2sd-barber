"""
Carrossel com Swiper.js.
"""
import streamlit as st
import streamlit.components.v1 as components
import base64
from pathlib import Path


def render_carousel(imagens, altura=450, autoplay=True, intervalo=4000):
    slides_html = []
    for img_path in imagens:
        path = Path(img_path)
        if not path.exists():
            continue
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        ext = path.suffix.lower().lstrip(".")
        if ext == "jpg":
            ext = "jpeg"
        slides_html.append(f'<div class="swiper-slide"><img src="data:image/{ext};base64,{b64}" /></div>')

    if not slides_html:
        st.info("📸 Adicione imagens à pasta assets/carousel/ para ver o carrossel.")
        return

    autoplay_js = f"{{ delay: {intervalo}, disableOnInteraction: false }}" if autoplay else "false"

    html = f'''
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <style>
        .swiper {{ width: 100%; height: {altura}px; border-radius: 16px; overflow: hidden; box-shadow: 0 8px 32px rgba(212,175,55,0.15); }}
        .swiper-slide img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
        .swiper-button-next, .swiper-button-prev {{ color: #D4AF37; background: rgba(0,0,0,0.5); width: 44px; height: 44px; border-radius: 50%; }}
        .swiper-button-next::after, .swiper-button-prev::after {{ font-size: 18px; font-weight: bold; }}
        .swiper-pagination-bullet {{ background: rgba(255,255,255,0.5); }}
        .swiper-pagination-bullet-active {{ background: #D4AF37; width: 24px; border-radius: 4px; }}
    </style>
    <div class="swiper mySwiper">
        <div class="swiper-wrapper">{''.join(slides_html)}</div>
        <div class="swiper-button-next"></div>
        <div class="swiper-button-prev"></div>
        <div class="swiper-pagination"></div>
    </div>
    <script>
        new Swiper('.mySwiper', {{
            loop: true, autoplay: {autoplay_js},
            pagination: {{ el: '.swiper-pagination', clickable: true }},
            navigation: {{ nextEl: '.swiper-button-next', prevEl: '.swiper-button-prev' }},
            effect: 'slide', speed: 600,
        }});
    </script>
    '''
    components.html(html, height=altura + 20)
