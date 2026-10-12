#!/usr/bin/env python3
"""Build the static website using Python's standard library. No runtime dependencies."""
from collections import defaultdict
from datetime import date
from html import escape
import json
import hashlib
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
PROFILE = json.loads((ROOT / 'data/profile.json').read_text())
PAPERS = json.loads((ROOT / 'data/publications.json').read_text())
UPDATED = date.fromisoformat(PROFILE['updated']).strftime('%B %-d, %Y')
CV_PREVIEW = []


def prepare_cv_preview():
    """Keep portable image previews tied to the exact downloadable PDF."""
    pdf = ROOT / 'assets/Jinhwan_Sul_CV.pdf'
    digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
    manifest = ROOT / 'assets/cv-preview.json'
    existing = json.loads(manifest.read_text()) if manifest.exists() else {}
    if existing.get('sha256') == digest and all((ROOT / 'assets' / p['file']).exists() for p in existing.get('pages', [])):
        return existing['pages']
    renderer = shutil.which('pdftoppm')
    if not renderer:
        print('PDF preview not regenerated: install Poppler (pdftoppm). PDF download remains available.')
        return []
    pages = []
    with tempfile.TemporaryDirectory() as directory:
        prefix = Path(directory) / 'cv-page'
        subprocess.run([renderer, '-scale-to', '1800', '-png', str(pdf), str(prefix)], check=True)
        for image in sorted(Path(directory).glob('cv-page-*.png'), key=lambda p: int(p.stem.rsplit('-', 1)[1])):
            width, height = struct.unpack('>II', image.read_bytes()[16:24])
            shutil.copyfile(image, ROOT / 'assets' / image.name)
            pages.append({'file': image.name, 'width': width, 'height': height})
    manifest.write_text(json.dumps({'sha256': digest, 'pages': pages}, indent=2) + '\n')
    return pages


def icon(name):
    paths = {
        'arrow': '<path d="M4 12h15m-6-6 6 6-6 6"/>',
        'external': '<path d="M7 17 17 7M7 7h10v10"/>',
        'mail': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/>',
        'pin': '<path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2"/>',
        'document': '<path d="M14 3H5v18h14V8Zm0 0v5h5M8 12h8m-8 4h6"/>',
        'scholar': '<path d="m2 9 10-5 10 5-10 5Zm4 2v6c3 3 9 3 12 0v-6m4-2v9"/>',
        'code': '<path d="m7 7-5 5 5 5m10-10 5 5-5 5m-4-13-2 16"/>',
        'linkedin': '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 10v7m0-10v.1m5 9.9v-7m0 3c0-4 5-4 5 0v4"/>',
        'download': '<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',
    }
    return f'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[name]}</svg>'


def external(url, label, class_name=''):
    return f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer" class="{class_name}">{label}</a>'


def profile(base, home=False):
    links = [('scholar', 'Google Scholar', PROFILE['scholar']), ('code', 'GitHub', PROFILE['github']), ('linkedin', 'LinkedIn', PROFILE['linkedin'])]
    socials = ''.join(external(url, icon(symbol) + label) for symbol, label, url in links)
    section_nav = ''
    if home:
        sections = [('about', 'About'), ('research', 'Research'), ('education', 'Education'), ('experience', 'Experience'), ('selected-publications', 'Selected publications'), ('honors', 'Honors & service'), ('contact', 'Contact')]
        section_nav = '<nav class="section-nav" aria-label="On this page">' + ''.join(f'<a href="#{key}">{label}</a>' for key, label in sections) + '</nav>'
    return f'''<aside class="profile" aria-label="Profile">
      <img class="portrait" src="{base}assets/jinhwan-sul.jpg" width="230" height="230" alt="Jinhwan Sul outdoors beside a waterfall" fetchpriority="high">
      <div class="profile-summary"><h2 class="profile-name">Jinhwan Sul</h2>
        <p class="profile-role">Ph.D. student in<br>Machine Learning</p>
        <p class="profile-school"><a href="https://www.gatech.edu/">Georgia Institute of Technology</a></p>
        <p class="profile-location">{icon('pin')}Atlanta, Georgia</p></div>
      <div class="profile-links"><a class="email" href="mailto:{PROFILE['email']}">{icon('mail')}{PROFILE['email']}</a>{socials}
        <a href="{base}cv/">{icon('document')}CV</a></div>
      {section_nav}
    </aside>'''


def page(title, content, active='About', base='./', path=''):
    navigation = [('About', base), ('Publications', base + 'publications/'), ('CV', base + 'cv/'), ('Contact', base + '#contact')]
    nav = ''.join(f'<a href="{url}"' + (' aria-current="page"' if label == active else '') + (' class="nav-contact"' if label == 'Contact' else '') + f'>{label}</a>' for label, url in navigation)
    canonical = PROFILE['url'] + '/' + path
    schema = {
        '@context': 'https://schema.org', '@type': 'ProfilePage',
        'dateModified': PROFILE['updated'],
        'mainEntity': {'@type': 'Person', 'name': PROFILE['name'], 'url': PROFILE['url'],
                       'image': PROFILE['url'] + '/assets/jinhwan-sul.jpg',
                       'jobTitle': PROFILE['role'], 'affiliation': {'@type': 'CollegeOrUniversity', 'name': PROFILE['institution']},
                       'sameAs': [PROFILE['github'], PROFILE['scholar'], PROFILE['linkedin']]}
    }
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#235f91">
  <title>{escape(title)} | Jinhwan Sul</title>
  <meta name="description" content="{escape(PROFILE['description'], quote=True)}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{escape(title)} | Jinhwan Sul">
  <meta property="og:description" content="{escape(PROFILE['description'], quote=True)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{PROFILE['url']}/assets/jinhwan-sul.jpg">
  <meta property="og:image:alt" content="Jinhwan Sul">
  <meta name="twitter:card" content="summary">
  <link rel="icon" type="image/svg+xml" href="{base}assets/favicon.svg">
  <link rel="stylesheet" href="{base}assets/styles.css">
  <script src="{base}assets/site.js" defer></script>
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head>
<body id="top">
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header"><div class="header-inner">
    <a class="brand" href="{base}">Jinhwan Sul<span>.</span></a>
    <nav class="primary-nav" aria-label="Main navigation">{nav}</nav>
  </div></header>
  <div class="site-layout">
    {profile(base, active == 'About')}
    <main id="main" class="main-content">{content}</main>
  </div>
  <footer class="site-footer"><span>© {PROFILE['updated'][:4]} Jinhwan Sul <span aria-hidden="true">·</span> Updated {UPDATED}</span><a class="back-top" href="#top">Back to top ↑</a></footer>
</body>
</html>
'''


def heading(title, extra=''):
    return f'<div class="section-heading"><h2>{title}</h2>{extra}</div>'


def timeline(dates, title, subtitle, detail=''):
    return f'<div class="timeline-row"><div class="timeline-date">{dates}</div><div class="timeline-content"><h3>{title}</h3><p>{subtitle}</p>' + (f'<p class="detail">{detail}</p>' if detail else '') + '</div></div>'


def publication(paper, selected=False):
    authors = ', '.join(f'<strong>{escape(a)}</strong>' if a.startswith('Jinhwan Sul') else escape(a) for a in paper['authors'])
    distinction = f'<span class="distinction">{escape(paper["distinction"])}</span>' if paper['distinction'] else ''
    paper_link = external(paper['url'], 'arXiv ↗' if paper['type'] == 'preprint' else 'Paper ↗')
    code_link = external(paper['code'], 'Code & data ↗') if paper['code'] else ''
    anchor = 'selected-' + paper['id'] if selected else paper['id']
    return f'''<article class="publication" id="{anchor}" data-publication data-topics="{' '.join(paper['topics'])}">
      <div class="publication-meta"><span class="venue">{escape(paper['venue'])}</span>{distinction}</div>
      <h3>{external(paper['url'], escape(paper['title']))}</h3>
      <p class="authors">{authors}</p>
      <div class="paper-links">{paper_link}{code_link}</div>
    </article>'''


def home_content():
    selected = ''.join(publication(next(p for p in PAPERS if p['id'] == id_), True) for id_ in ['gallop', 'drsb', 'asbm', 'summdiff'])
    return f'''
    <section id="about" aria-labelledby="about-heading">
      <p class="eyebrow">Optimization &amp; Machine Learning</p>
      <h1 class="page-title" id="about-heading">About me</h1>
      <div class="about-copy">
        <p>I am a Ph.D. student in <strong>Machine Learning</strong> at the <a href="https://www.gatech.edu/">Georgia Institute of Technology</a>, advised by <strong>Prof. Evangelos A. Theodorou</strong> in the <a href="https://sites.gatech.edu/acds/">Autonomous Control and Decision Systems (ACDS) Laboratory</a>.</p>
        <p class="research-statement">I develop machine learning methods for large-scale optimization through the lens of optimal control theory.</p>
        <p>My research focuses on <strong>GPU-based optimization</strong>, <strong>reinforcement learning for solver acceleration</strong>, and <strong>robust generative models</strong>. I am interested in how learning and control can make computational methods more efficient and reliable.</p>
        <p>Previously, I worked with Prof. Joonseok Lee at Seoul National University on video summarization and molecular representation learning, and with Prof. Yan Wang at Georgia Tech on quantum scientific computing. I received my B.S. degrees in Computer Science and Engineering and Mechanical Engineering from Seoul National University.</p>
      </div>
      <div class="actions"><a class="button" href="./cv/">{icon('document')}View CV</a><a class="button secondary" href="./publications/">Publications {icon('arrow')}</a><a class="text-link" href="mailto:{PROFILE['email']}">Get in touch {icon('external')}</a></div>
    </section>

    <section class="section" id="research" aria-labelledby="research-heading">
      <div class="section-heading"><h2 id="research-heading">Research</h2></div>
      <div class="interest-columns">
        <div><h3>Optimization</h3><p>Large-scale optimization<br>GPU-based algorithms<br>Stochastic optimal control<br>Linear &amp; mixed integer programming</p></div>
        <div><h3>Machine learning</h3><p>ML for Optimization<br>Reinforcement learning<br>Schrödinger bridge<br>Diffusion-based generative models</p></div>
      </div>
      <article class="research-item"><p class="small-label">Learning to accelerate optimization</p><h3>GALLOP: reinforcement learning for linear programming</h3><p>I formulate solver acceleration as an optimal control problem and train feedback policies to coordinate solver parameters and restarts, while retaining GPU-friendly matrix–vector products and projections.</p><a class="text-link" href="./publications/#gallop">Read the preprint {icon('arrow')}</a></article>
      <article class="research-item"><p class="small-label">Robust generative modeling · DARPA AIQ</p><h3>Distributionally Robust Schrödinger Bridge</h3><p>I develop distributionally robust fine-tuning methods for diffusion-based Schrödinger bridge models, studying resilience to noisy and shifted inputs without test-time retraining.</p><a class="text-link" href="./publications/#drsb">Read the preprint {icon('arrow')}</a></article>
      <article class="research-item"><p class="small-label">Large-scale robust optimization</p><h3>Robust inventory management</h3><p>I formulate multi-item inventory problems as sparse robust linear programs and study solver performance and decomposition. Using Dantzig–Wolfe column generation, I solved an instance with 50,000 items.</p></article>
    </section>

    <section class="section" id="education">
      {heading('Education')}
      {timeline('2025 – present', 'Georgia Institute of Technology', 'Ph.D. in Machine Learning', 'ACDS Laboratory · Advisor: Prof. Evangelos A. Theodorou<br>Expected graduation: Spring 2029')}
      {timeline('2020 – 2023', 'Seoul National University', 'B.S. in Computer Science and Engineering')}
      {timeline('2016 – 2023', 'Seoul National University', 'B.S. in Mechanical Engineering')}
      {timeline('2013 – 2016', 'Gyeonggi Science High School for the Gifted', '')}
    </section>

    <section class="section" id="experience">
      {heading('Research &amp; experience')}
      {timeline('Jan 2025 – present', 'Georgia Institute of Technology', 'Doctoral Research · ACDS Laboratory', 'Advisor: Prof. Evangelos A. Theodorou<br>GPU-based optimization, reinforcement learning for solver acceleration, robust inventory optimization, and distributionally robust generative modeling.')}
      {timeline('Jun 2023 – Dec 2024', 'Georgia Institute of Technology', 'Prior Research · Prof. Yan Wang', 'Quantum methods for differential equations and scientific computing; machine learning for semiconductor and additive manufacturing process monitoring.')}
      {timeline('Feb 2022 – Sep 2024', 'Seoul National University', 'Research Internship &amp; Collaboration · Prof. Joonseok Lee', 'Generative video summarization, the Mr. HiSum dataset, and physically regularized molecular representation learning.')}
      {timeline('Jan – Feb 2020', 'Samsung C-Lab', 'Intern · Seoul, Korea', 'Supported a long-range wireless charging project through rectifier-circuit and heat-transfer experiments and a review of wireless power transmission patents.')}
    </section>

    <section class="section" id="selected-publications">
      {heading('Selected publications', '<a class="text-link" href="./publications/">All 9 publications ' + icon('arrow') + '</a>')}
      {selected}
      <p class="publication-note">* Equal contribution. See the <a href="./publications/">full publication list</a> for earlier work.</p>
    </section>

    <section class="section" id="honors">
      {heading('Honors &amp; scholarships')}
      <ul class="compact-list">
        <li><time>2024</time><div><strong>Best Paper Award, 3rd Place</strong><span class="detail">Quantum Applications Track · IEEE QCE</span></div></li>
        <li><time>2021</time><div><strong>2nd Place, Graph Pattern Matching Challenge</strong><span class="detail">Seoul National University · More than 60 teams</span></div></li>
        <li><time>2021</time><div><strong>Special Prize, SNU X-Corps Research Competition</strong><span class="detail">Hydrogen and floating-photovoltaic electricity supply system</span></div></li>
        <li><time>2020–21</time><div><strong>Kwanjeong Education Foundation Scholarship</strong><span class="detail">Full tuition and study subsidy · Spring 2020–Fall 2021</span></div></li>
        <li><time>2017</time><div><strong>Eminence Scholarship</strong><span class="detail">Seoul National University · Full tuition, Spring 2017</span></div></li>
        <li><time>2016–19</time><div><strong>Merit-Based Scholarships</strong><span class="detail">Seoul National University · Fall 2019, Fall 2016, and Spring 2016</span></div></li>
      </ul>
    </section>

    <section class="section" id="talks-service">
      {heading('Talks &amp; service')}
      <div class="two-column">
        <div><h3>Invited talks &amp; presentations</h3><p><strong>Quantum Functional Expansion to Solve Stochastic Differential Equations</strong><br>Invited talk · IEEE Quantum Week 2024 Review Workshop, The Institute of Semiconductor Engineers, Korea (online) · Nov 2024</p><p><strong>Quantum Solver of Stochastic Differential Equations</strong><br>Conference presentation · WCCM 2024</p></div>
        <div><h3>Reviewer</h3><p>ICLR · 2027 cycle<br>NeurIPS Datasets and Benchmarks · 2023, 2024, 2026<br>WACV · 2024</p><h3>Teaching</h3><p>Engineering Mathematics 2 · 2020–21<br>Foundation of Physics 2 · 2019<br>Seoul National University</p></div>
      </div>
    </section>

    <section class="section" id="patent">
      {heading('Patent application')}
      <div class="timeline-content"><h3>Quantum Functional Expansion System for Quantum Scientific Computing</h3><p class="detail">Co-inventor · U.S. Provisional Patent Application No. 63/692,936<br>Filed September 10, 2024</p></div>
    </section>

    <section class="section" id="skills">
      {heading('Technical skills')}
      <dl class="skills-list">
        <dt>Optimization</dt><dd>Gurobi, HiGHS, NVIDIA cuOpt, CVXPY, OSQP, MPAX; PDHG/PDLP, ADMM</dd>
        <dt>Machine learning</dt><dd>JAX, Flax, PyTorch; RL/PPO, optimal transport, diffusion models</dd>
        <dt>Computing</dt><dd>Python, C/C++, MATLAB, Java; NumPy, SciPy; GPU computing, sparse linear algebra</dd>
        <dt>Research software</dt><dd>Git, pytest, Hydra</dd>
        <dt>Languages</dt><dd>Korean (native), English (fluent)</dd>
      </dl>
    </section>

    <section class="contact" id="contact">
      <h2>Get in touch</h2><p>For research conversations and professional inquiries, email is the best way to reach me.</p>
      <a href="mailto:{PROFILE['email']}">{PROFILE['email']} {icon('external')}</a>
    </section>'''


def publications_content():
    groups = defaultdict(list)
    for paper in PAPERS:
        groups[paper['year']].append(paper)
    sections = ''.join(f'<section class="year-group" data-year-group aria-labelledby="year-{year}"><h2 class="year-heading" id="year-{year}">{year}</h2><div>' + ''.join(publication(p) for p in papers) + '</div></section>' for year, papers in sorted(groups.items(), reverse=True))
    filters = [('all', 'All'), ('optimization', 'Optimization'), ('generative-models', 'Generative models'), ('video', 'Video understanding'), ('scientific-computing', 'Scientific computing')]
    buttons = ''.join(f'<button type="button" data-filter="{key}" aria-pressed="{str(key == "all").lower()}">{label}</button>' for key, label in filters)
    return f'''
      <p class="eyebrow">Research output</p><h1 class="page-title">Publications</h1>
      <p class="page-intro">My work in optimization, generative modeling, video understanding, and scientific computing. Listed by year, including preprints.</p>
      <a class="text-link" href="{PROFILE['scholar']}" target="_blank" rel="noopener noreferrer">View Google Scholar {icon('external')}</a>
      <div class="publication-tools" data-publication-filters hidden>
        <label for="publication-search" class="search-label">Search publications</label>
        <input type="search" class="search-input" id="publication-search" placeholder="Search by title, author, or venue…" autocomplete="off" aria-controls="publication-list">
        <div class="filter-buttons" role="group" aria-label="Filter by research area">{buttons}</div>
        <p class="result-count" role="status" aria-live="polite" data-result-count>{len(PAPERS)} of {len(PAPERS)} publications</p>
      </div>
      <p class="publication-note">* Equal contribution. Preprints are labeled separately from conference and journal publications.</p>
      <div id="publication-list">{sections}</div>
      <div class="empty-state" data-empty hidden><p>No publications match your search.</p><button type="button" data-reset-filters>Clear search and filters</button></div>'''


def cv_content():
    previews = ''.join(f'<figure class="cv-page"><a href="../assets/Jinhwan_Sul_CV.pdf#page={i}" target="_blank" rel="noopener" aria-label="Open CV page {i} in the original PDF"><img src="../assets/{p["file"]}" width="{p["width"]}" height="{p["height"]}" loading="lazy" alt="CV page {i} of {len(CV_PREVIEW)}. Open the original PDF for selectable text."></a><figcaption>Page {i} of {len(CV_PREVIEW)}</figcaption></figure>' for i, p in enumerate(CV_PREVIEW, 1))
    return f'''
      <p class="eyebrow">Education, research &amp; experience</p><h1 class="page-title">Curriculum vitae</h1>
      <p class="page-intro">My complete academic and research record, including publications, research experience, honors, teaching, and technical skills.</p>
      <div class="actions"><a class="button" href="../assets/Jinhwan_Sul_CV.pdf" download="Jinhwan_Sul_CV.pdf">{icon('download')}Download CV</a><a class="button secondary" href="../assets/Jinhwan_Sul_CV.pdf" target="_blank" rel="noopener">Open PDF {icon('external')}</a></div>
      <div class="cv-overview"><h2>At a glance</h2><p><strong>Current:</strong> Ph.D. in Machine Learning, Georgia Institute of Technology</p><p><strong>Research:</strong> Large-scale optimization, optimal control, and machine learning</p><p><strong>Advisor:</strong> Prof. Evangelos A. Theodorou · ACDS Laboratory</p><p><strong>Education:</strong> B.S. degrees in Computer Science and Engineering and Mechanical Engineering, Seoul National University</p></div>
      <div class="pdf-header"><h2>CV preview</h2><span>Updated {UPDATED} · PDF</span></div>
      <p class="pdf-fallback">Select a page to open the original PDF with selectable text, or read the <a href="../#education">web overview</a>.</p>
      <div class="cv-preview">{previews or '<p><a href="../assets/Jinhwan_Sul_CV.pdf">Open the CV PDF</a></p>'}</div>'''


def build():
    global CV_PREVIEW
    CV_PREVIEW = prepare_cv_preview()
    (ROOT / 'publications').mkdir(exist_ok=True)
    (ROOT / 'cv').mkdir(exist_ok=True)
    (ROOT / 'index.html').write_text(page('About', home_content()), encoding='utf-8')
    (ROOT / 'publications/index.html').write_text(page('Publications', publications_content(), 'Publications', '../', 'publications/'), encoding='utf-8')
    (ROOT / 'cv/index.html').write_text(page('Curriculum vitae', cv_content(), 'CV', '../', 'cv/'), encoding='utf-8')
    error = '<div class="not-found"><p class="eyebrow">404</p><h1 class="page-title">Page not found</h1><p>The page may have moved. You can find my research, publications, and CV on the homepage.</p><a class="button" href="/">Return to About</a></div>'
    (ROOT / '404.html').write_text(page('Page not found', error, '', '/', '404.html').replace('<meta name="description"', '<meta name="robots" content="noindex"><meta name="description"'), encoding='utf-8')
    urls = ['', 'publications/', 'cv/']
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{PROFILE["url"]}/{path}</loc><lastmod>{PROFILE["updated"]}</lastmod></url>' for path in urls) + '</urlset>\n'
    (ROOT / 'sitemap.xml').write_text(sitemap, encoding='utf-8')
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {PROFILE["url"]}/sitemap.xml\n', encoding='utf-8')
    print(f'Built About, Publications ({len(PAPERS)} papers), CV, 404, sitemap, and robots.txt.')


if __name__ == '__main__':
    build()
