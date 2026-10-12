(() => {
  'use strict';
  const filterBar = document.querySelector('[data-publication-filters]');
  if (filterBar) {
    filterBar.hidden = false;
    const search = document.querySelector('#publication-search');
    const buttons = [...filterBar.querySelectorAll('[data-filter]')];
    const entries = [...document.querySelectorAll('[data-publication]')];
    const groups = [...document.querySelectorAll('[data-year-group]')];
    const count = document.querySelector('[data-result-count]');
    const empty = document.querySelector('[data-empty]');
    let selected = 'all';
    function filter() {
      const query = search.value.toLocaleLowerCase().trim();
      let visible = 0;
      entries.forEach(entry => {
        const matchesTopic = selected === 'all' || entry.dataset.topics.split(' ').includes(selected);
        const matchesSearch = entry.textContent.toLocaleLowerCase().includes(query);
        entry.hidden = !(matchesTopic && matchesSearch);
        if (!entry.hidden) visible++;
      });
      groups.forEach(group => {
        group.hidden = ![...group.querySelectorAll('[data-publication]')].some(entry => !entry.hidden);
      });
      count.textContent = `${visible} of ${entries.length} publications`;
      empty.hidden = visible > 0;
    }
    buttons.forEach(button => button.addEventListener('click', () => {
      selected = button.dataset.filter;
      buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      filter();
    }));
    search.addEventListener('input', filter);
    document.querySelector('[data-reset-filters]').addEventListener('click', () => {
      search.value = '';
      buttons[0].click();
      search.focus();
    });
  }
  const sectionLinks = [...document.querySelectorAll('.section-nav a')];
  if (sectionLinks.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          sectionLinks.forEach(link => {
            if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'location');
            else link.removeAttribute('aria-current');
          });
        }
      });
    }, { rootMargin: '-12% 0px -64% 0px', threshold: 0 });
    sectionLinks.forEach(link => {
      const target = document.getElementById(link.hash.slice(1));
      if (target) observer.observe(target);
    });
  }
})();
