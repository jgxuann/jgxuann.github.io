(() => {
  const normalizeTitle = (title) => title
    .toLowerCase()
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();

  const counters = [...document.querySelectorAll('[data-google-scholar-title]')];
  if (!counters.length) return;

  fetch('./assets/data/google-scholar-citations.json', { cache: 'no-store' })
    .then((response) => {
      if (!response.ok) throw new Error(`Citation data request failed: ${response.status}`);
      return response.json();
    })
    .then((data) => {
      const citationsByTitle = new Map(
        Object.entries(data.papers || {}).map(([title, citations]) => [normalizeTitle(title), citations])
      );

      counters.forEach((counter) => {
        const citations = citationsByTitle.get(normalizeTitle(counter.dataset.googleScholarTitle));
        counter.querySelector('.citation-badge-value').textContent = Number.isInteger(citations) ? citations : '—';
        counter.title = Number.isInteger(citations)
          ? `Google Scholar citations; updated ${new Date(data.updated_at).toLocaleString()}`
          : 'This paper was not found in the latest Google Scholar export.';
      });

      document.querySelectorAll('[data-google-scholar-total]').forEach((counter) => {
        counter.querySelector('.citation-badge-value').textContent = Number.isInteger(data.total_citations)
          ? data.total_citations
          : '—';
        counter.title = Number.isInteger(data.total_citations)
          ? `Total Google Scholar citations; updated ${new Date(data.updated_at).toLocaleString()}`
          : 'Google Scholar total citations are unavailable.';
      });
    })
    .catch(() => {
      counters.forEach((counter) => {
        counter.querySelector('.citation-badge-value').textContent = '—';
        counter.title = 'Google Scholar citation data is temporarily unavailable.';
      });
      document.querySelectorAll('[data-google-scholar-total]').forEach((counter) => {
        counter.querySelector('.citation-badge-value').textContent = '—';
        counter.title = 'Google Scholar total citations are temporarily unavailable.';
      });
    });
})();
