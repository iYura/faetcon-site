#!/usr/bin/env python3
"""Генератор статичного сайту FAETCon. Запуск: python3 build.py
Читає HTML-фрагменти з content/<lang>/*.html, обгортає в templates/base.html,
пише готові сторінки в ../docs/ (GitHub Pages). Без зовнішніх залежностей."""

import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "..", "docs")
CONTENT = os.path.join(ROOT, "content")
TEMPLATE_PATH = os.path.join(ROOT, "templates", "base.html")

EVENT = {
    "name": "FAETCon",
    "full_uk": "ФАЕТ Конференція",
    "date_uk": "28 жовтня 2026",
    "date_en": "October 28, 2026",
    "venue": "КАІ, Київ",
    "venue_en": "KAI, Kyiv",
}

# slug, (nav_uk, nav_en), у групі "Долучайся!"/"Get involved" чи ні
PAGES = [
    ("index",                    "Головна",        "Home",              None),
    ("program/index",            "Програма",       "Program",           None),
    ("talks/index",               "Доповіді",       "Talks",             None),
    ("badge/index",               "Бейдж",          "Badge",             None),
    ("vendors/index",             "Учасники",       "Vendors",           None),
    ("sponsors/index",            "Спонсори",       "Sponsors",          None),
    ("tickets/index",             "Квитки",         "Tickets",           None),
    ("venue/index",               "Локація",        "Venue",             None),
    ("get-involved/index",        "Долучайся!",     "Get involved",      "group"),
    ("get-involved/spread-the-word/index", "Розкажи друзям", "Spread the word", "sub"),
    ("get-involved/volunteer/index",       "Волонтерити",    "Volunteer",       "sub"),
    ("faq/index",                 "FAQ",            "FAQ",               None),
    ("contacts/index",            "Контакти",       "Contacts",          None),
]

# Пункти, що показуються в самій навбарі (без підменю "Долучайся!")
TOP_NAV_SLUGS = [
    "index", "program/index", "talks/index", "badge/index", "vendors/index",
    "sponsors/index", "tickets/index", "venue/index",
]

GET_INVOLVED_MENU = [
    ("get-involved/spread-the-word/index", "Розкажи друзям", "Spread the word"),
    ("sponsors/index", "Стати спонсором", "Become a sponsor"),
    ("vendors/index", "Взяти стенд", "Get a vendor booth"),
    ("talks/index", "Подати доповідь", "Submit a talk"),
    ("get-involved/volunteer/index", "Волонтерити", "Volunteer"),
]

TITLES = {
    "index":        ("Головна", "Home"),
    "program/index": ("Програма", "Program"),
    "talks/index":   ("Доповіді", "Talks"),
    "badge/index":   ("Бейдж", "Badge"),
    "vendors/index": ("Учасники", "Vendors"),
    "sponsors/index": ("Спонсори", "Sponsors"),
    "tickets/index": ("Квитки", "Tickets"),
    "venue/index":   ("Локація", "Venue"),
    "get-involved/index": ("Долучайся!", "Get involved"),
    "get-involved/spread-the-word/index": ("Розкажи друзям", "Spread the word"),
    "get-involved/volunteer/index": ("Волонтерити", "Volunteer"),
    "faq/index":     ("FAQ", "FAQ"),
    "contacts/index": ("Контакти", "Contacts"),
}


def depth_of(slug):
    return slug.count("/")


def rel_prefix(slug):
    return "../" * depth_of(slug)


def build_nav(current_slug, lang):
    prefix = rel_prefix(current_slug)
    other_prefix = "" if lang == "uk" else ""
    items = []
    for slug in TOP_NAV_SLUGS:
        label_uk, label_en = TITLES[slug]
        label = label_uk if lang == "uk" else label_en
        href = f"{prefix}{slug}.html"
        active = " class=\"active\"" if slug == current_slug else ""
        items.append(f'<a href="{href}"{active}>{label}</a>')

    gi_active = " nav-group-toggle active" if current_slug.startswith("get-involved/") or current_slug == "get-involved/index" else " nav-group-toggle"
    gi_label = "Долучайся!" if lang == "uk" else "Get involved"
    menu_items = []
    for slug, label_uk, label_en in GET_INVOLVED_MENU:
        label = label_uk if lang == "uk" else label_en
        href = f"{prefix}{slug}.html"
        menu_items.append(f'<a href="{href}">{label}</a>')
    gi_href = f"{prefix}get-involved/index.html"
    items.append(
        f'<span class="nav-group"><a href="{gi_href}" class="{gi_active.strip()}">{gi_label} '
        f'<span class="caret" aria-hidden="true">▾</span></a>'
        f'<span class="nav-group-menu">{"".join(menu_items)}</span></span>'
    )

    for slug in ("faq/index", "contacts/index"):
        label_uk, label_en = TITLES[slug]
        label = label_uk if lang == "uk" else label_en
        href = f"{prefix}{slug}.html"
        active = " class=\"active\"" if slug == current_slug else ""
        items.append(f'<a href="{href}"{active}>{label}</a>')

    return "".join(items)


def build_lang_switch(current_slug, lang):
    prefix = rel_prefix(current_slug)
    if lang == "uk":
        return (
            '<div class="lang-switch"><span class="lang-current">UA</span>'
            f'<a href="{prefix}en/{current_slug}.html" class="lang-link">EN</a></div>'
        )
    else:
        # current_slug для en включає "en/" на початку? Ні — ведемо облік однаково,
        # але фізичний шлях en-файлів має on додатковий рівень "en/".
        return (
            '<div class="lang-switch">'
            f'<a href="{prefix}{current_slug}.html" class="lang-link">UA</a>'
            '<span class="lang-current">EN</span></div>'
        )


def main():
    if os.path.isdir(SITE):
        for name in os.listdir(SITE):
            path = os.path.join(SITE, name)
            if name == "assets":
                continue
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = f.read()

    for lang, lang_attr, out_root in (("uk", "uk", SITE), ("en", "en", os.path.join(SITE, "en"))):
        content_dir = os.path.join(CONTENT, lang)
        for slug, *_ in PAGES:
            content_path = os.path.join(content_dir, slug + ".html")
            if not os.path.exists(content_path):
                print(f"[!] Пропущено (немає контенту): {lang}/{slug}")
                continue
            with open(content_path, encoding="utf-8") as f:
                body = f.read()

            title_uk, title_en = TITLES[slug]
            title = title_uk if lang == "uk" else title_en
            page_title = f"{title} — {EVENT['name']}" if slug != "index" else f"Головна — {EVENT['name']}" if lang == "uk" else f"Home — {EVENT['name']}"

            nav_slug = slug
            nav_html = build_nav(nav_slug, lang)

            if lang == "uk":
                logo_href = f"{rel_prefix(slug)}index.html"
                lang_switch = (
                    '<div class="lang-switch"><span class="lang-current">UA</span>'
                    f'<a href="{rel_prefix(slug)}en/{slug}.html" class="lang-link">EN</a></div>'
                )
                css_href = f"{rel_prefix(slug)}assets/css/style.css"
                canonical = f"https://iyura.github.io/faetcon-site/{slug}.html"
            else:
                logo_href = f"{rel_prefix(slug)}index.html"
                lang_switch = (
                    '<div class="lang-switch">'
                    f'<a href="{rel_prefix(slug)}../{slug}.html" class="lang-link">UA</a>'
                    '<span class="lang-current">EN</span></div>'
                )
                css_href = f"{rel_prefix(slug)}../assets/css/style.css"
                canonical = f"https://iyura.github.io/faetcon-site/en/{slug}.html"

            html = (
                template
                .replace("{{lang}}", lang_attr)
                .replace("{{page_title}}", page_title)
                .replace("{{css_href}}", css_href)
                .replace("{{logo_href}}", logo_href)
                .replace("{{nav}}", nav_html)
                .replace("{{lang_switch}}", lang_switch)
                .replace("{{canonical}}", canonical)
                .replace("{{body}}", body)
                .replace("{{footer_org_uk_href}}", f"{rel_prefix(slug)}contacts/index.html" if lang == "uk" else f"{rel_prefix(slug)}../contacts/index.html")
            )

            out_path = os.path.join(out_root, slug + ".html")
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"  ✓ {os.path.relpath(out_path, SITE)}")

    print("\nГотово. Відкрий:", os.path.join(SITE, "index.html"))


if __name__ == "__main__":
    main()
