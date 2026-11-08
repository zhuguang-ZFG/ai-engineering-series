"""Render the original book's hand drawings and check text at reading size."""
import json
import os
import shutil
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'tmp/illustration-polish-02'
SLUGS = ['learn-path', 'funnel', 'jtbd', 'error-flow', 'deploy', 'db-index', 'git-history', 'web-framework']


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault('PLAYWRIGHT_NODEJS_PATH', shutil.which('node'))
    if os.name == 'nt':
        os.environ['NODE_OPTIONS'] = '--preserve-symlinks --preserve-symlinks-main'
    report = {'figures': [], 'failures': []}
    panels = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=os.environ.get('COURSE_BROWSER_CHANNEL', 'chrome'), headless=True)
        page = browser.new_page(viewport={'width': 1000, 'height': 1000}, device_scale_factor=2)
        page.context.set_offline(True)
        for slug in SLUGS:
            source = ROOT / 'book/assets/handdraw' / f'{slug}.svg'
            page.goto(source.as_uri())
            result = page.evaluate('''() => {
              const svg=document.documentElement, frame=svg.viewBox.baseVal;
              const nodes=[...svg.querySelectorAll(':scope > g text')];
              const bounds=nodes.map(el=>({el,text:el.textContent,...Object.fromEntries(['x','y','width','height'].map(k=>[k,el.getBBox()[k]]))}));
              const outside=bounds.filter(b=>b.x < 0 || b.y < 0 || b.x+b.width > frame.width || b.y+b.height > frame.height).map(b=>b.text);
              const overlaps=[];
              for(let a=0;a<bounds.length;a++)for(let b=a+1;b<bounds.length;b++){
                const x=bounds[a],y=bounds[b];
                if(Math.min(x.x+x.width,y.x+y.width)-Math.max(x.x,y.x)>1 && Math.min(x.y+x.height,y.y+y.height)-Math.max(x.y,y.y)>1)overlaps.push([x.text,y.text]);
              }
              return {width:frame.width,height:frame.height,outside,overlaps,minLabel:Math.min(...nodes.map(n=>parseFloat(getComputedStyle(n).fontSize)))};
            }''')
            report['figures'].append({'name': slug, **result, 'labelAt320px': result['minLabel'] * 288 / result['width']})
            if result['outside'] or result['overlaps'] or result['minLabel'] < 26:
                report['failures'].append({'name': slug, **result})
            output = OUTPUT / f'{slug}.png'
            page.locator('svg').screenshot(path=str(output))
            im = Image.open(output).convert('RGB')
            im.thumbnail((480, 640))
            panels.append(im)
        browser.close()
    sheet = Image.new('RGB', (480 * 4, 640 * 2), '#fbfaf6')
    for i, im in enumerate(panels):
        sheet.paste(im, ((i % 4) * 480, (i // 4) * 640))
    sheet.save(OUTPUT / 'contact.png')
    (OUTPUT / 'figures.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    assert not report['failures'], json.dumps(report['failures'], ensure_ascii=False)
    print(f'Passed {len(SLUGS)} SVGs: 3:4 canvas, labels >= 26px, no text overlap or clipping')


if __name__ == '__main__':
    run()
