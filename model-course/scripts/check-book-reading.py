"""Check the original book's links, reflow and offline assets in real Chrome."""
import json
import os
import shutil
from pathlib import Path
from urllib.parse import unquote, urlsplit

from lxml import html
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tmp/original-review'


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    pages = sorted((ROOT / 'exports/book').glob('*.html'))
    pages += [ROOT / '开始阅读.html', ROOT / 'exports/landing.html']
    ids = {}
    links = 0
    chapter_structure = 0
    for path in pages:
        tree = html.fromstring(path.read_text(encoding='utf-8'))
        found = tree.xpath('//@id')
        assert len(found) == len(set(found)), (path.name, 'duplicate IDs')
        ids[path.resolve()] = set(found)
        if path.name.startswith('chapter-'):
            headings = tree.xpath('//article//*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5 or self::h6]')
            assert len(tree.xpath('//article/h1')) == 1, (path.name, 'chapter title')
            assert headings[0].tag == 'h1', (path.name, 'title before sections')
            for previous, current in zip(headings, headings[1:]):
                assert int(current.tag[1]) <= int(previous.tag[1]) + 1, (path.name, previous.text_content(), current.text_content())
            details = tree.xpath('//details[@class="contents"]')
            if details:
                assert details[0].getprevious().tag == 'h1', (path.name, 'TOC after title')
            chapter_structure += 1
    for path in pages:
        tree = html.fromstring(path.read_text(encoding='utf-8'))
        for href in tree.xpath('//@href | //@src'):
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc:
                continue
            target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path.resolve()
            assert target.exists(), (path.name, href)
            if parsed.fragment and target in ids:
                assert unquote(parsed.fragment) in ids[target], (path.name, href)
            links += 1
    os.environ.setdefault('PLAYWRIGHT_NODEJS_PATH', shutil.which('node'))
    if os.name == 'nt':
        os.environ['NODE_OPTIONS'] = '--preserve-symlinks --preserve-symlinks-main'
    report = {'pages': len(pages), 'localLinksAndAssets': links, 'chapterStructure': chapter_structure, 'layouts': [], 'failures': []}
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=os.environ.get('COURSE_BROWSER_CHANNEL', 'chrome'), headless=True)
        context = browser.new_context(viewport={'width': 320, 'height': 900}, reduced_motion='reduce')
        context.set_offline(True)
        page = context.new_page()
        for index, path in enumerate(pages):
            page.goto(path.as_uri(), wait_until='load')
            page.evaluate('''async () => {
              await Promise.all([...document.images].map(img => {img.loading='eager';return img.decode().catch(()=>{});}));
            }''')
            failed_images = page.evaluate('''() => [...document.images].filter(i=>!i.naturalWidth).map(i=>i.getAttribute('src'))''')
            if failed_images:
                report['failures'].append({'page': path.name, 'images': failed_images})
            for width, size in [(320, 18), (375, 24), (768, 18), (1440, 18)]:
                page.set_viewport_size({'width': width, 'height': 900})
                page.evaluate('(size)=>document.documentElement.style.fontSize=size+"px"', size)
                result = page.evaluate('''() => ({
                  width:document.documentElement.clientWidth, scroll:document.documentElement.scrollWidth,
                  unwrappedProse:[...document.querySelectorAll('pre.prose-block')].filter(el=>el.scrollWidth>el.clientWidth+1).length,
                  overflow:[...document.querySelectorAll('article p,article figure,article img,.table-scroll,article pre')]
                    .filter(el=>{const r=el.getBoundingClientRect();return r.width && (r.left < -1 || r.right > innerWidth+1);})
                    .slice(0,8).map(el=>({tag:el.tagName,text:el.textContent.slice(0,90)}))
                })''')
                report['layouts'].append({'page': path.name, 'width': width, 'font': size})
                if result['scroll'] > result['width'] + 1 or result['overflow'] or result['unwrappedProse']:
                    report['failures'].append({'page': path.name, 'width': width, 'font': size, **result})
            if index % 40 == 0:
                print(f'Checked {index+1}/{len(pages)} pages', flush=True)
        page.goto((ROOT / '开始阅读.html').as_uri())
        page.locator('.primary').click()
        assert page.url.endswith('exports/llm/course.html')
        assert page.locator('h1').inner_text() == '大模型：从入门到精通'
        page.goto((ROOT / '开始阅读.html').as_uri())
        page.locator('#original-book-link').click()
        assert page.url.endswith('exports/book/index.html')
        page.get_by_role('link', name='常见问题与排错', exact=True).click()
        assert page.locator('h1').inner_text() == '常见问题与排错'
        page.locator('.skip').focus()
        page.keyboard.press('Enter')
        assert page.evaluate('document.activeElement.id') == 'main'
        report['navigation'] = ['LLM primary entry', 'original book supplementary entry', 'chapter TOC link', 'keyboard skip']
        # Native disclosure, anchor navigation and figures must also work without JS.
        offline = browser.new_context(java_script_enabled=False, viewport={'width':375, 'height':900})
        offline.set_offline(True)
        reader = offline.new_page()
        reader.goto((ROOT / 'exports/book/chapter-020.html').as_uri())
        reader.locator('.contents summary').focus()
        reader.keyboard.press('Enter')
        assert reader.locator('.contents').get_attribute('open') is not None
        nested = reader.locator('.contents ul ul a').first
        target = nested.get_attribute('href')
        nested.click()
        assert unquote(urlsplit(reader.url).fragment) == target[1:]
        reader.goto((ROOT / 'exports/book/chapter-017.html').as_uri())
        assert len(reader.locator('h1').all()) == 1
        assert not reader.get_by_role('heading', name='常见问题与排错', exact=True).count() > 1
        reader.locator('.figure-zoom').first.click()
        assert reader.url.endswith('/error-flow.svg')
        report['navigation'] += ['nested TOC with keyboard, offline and no JS', 'full-size figure offline and no JS']
        offline.close()
        browser.close()
    (OUT / 'reading.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    assert not report['failures'], json.dumps(report['failures'][:15], ensure_ascii=False)
    print(f'Passed {len(pages)} pages / {len(report["layouts"])} layouts / {links} local links and assets')


if __name__ == '__main__':
    run()
