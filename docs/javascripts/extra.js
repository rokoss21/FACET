// FACET Documentation JavaScript Enhancements

// Add copy button to code blocks
document.addEventListener('DOMContentLoaded', function() {
  // Enhanced code block interactions
  const codeBlocks = document.querySelectorAll('pre');

  codeBlocks.forEach(function(block) {
    // Add language label if missing
    const code = block.querySelector('code');
    if (code && code.className && !block.querySelector('.code-label')) {
      const language = code.className.replace('language-', '');
      if (language !== 'language-') {
        const label = document.createElement('span');
        label.className = 'code-label';
        label.textContent = language.toUpperCase();
        label.style.cssText = `
          position: absolute;
          top: 0.5rem;
          right: 0.5rem;
          background: rgba(0,0,0,0.7);
          color: white;
          padding: 0.2rem 0.5rem;
          border-radius: 0.2rem;
          font-size: 0.8rem;
          font-weight: bold;
        `;
        block.style.position = 'relative';
        block.appendChild(label);
      }
    }
  });

  // Add syntax highlighting hints for FACET
  const facetBlocks = document.querySelectorAll('.language-facet');
  facetBlocks.forEach(function(block) {
    if (!block.querySelector('.facet-hint')) {
      const hint = document.createElement('div');
      hint.className = 'facet-hint';
      hint.innerHTML = `
        <small style="color: #666; font-style: italic;">
          💡 FACET syntax: <code>@facet</code> for blocks,
          <code>|> lens</code> for transforms,
          <code>&anchor</code>/<code>*alias</code> for references
        </small>
      `;
      hint.style.cssText = `
        margin-top: -0.5rem;
        margin-bottom: 1rem;
        padding: 0.5rem;
        background: #f0f8ff;
        border-left: 3px solid #0066cc;
        border-radius: 0.2rem;
      `;
      block.parentNode.insertBefore(hint, block);
    }
  });
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(event) {
  // Ctrl/Cmd + K to focus search
  if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
    event.preventDefault();
    const searchInput = document.querySelector('.md-search__input');
    if (searchInput) {
      searchInput.focus();
    }
  }
});

// Enhanced table of contents interaction
document.addEventListener('DOMContentLoaded', function() {
  const tocLinks = document.querySelectorAll('.md-nav__link');

  tocLinks.forEach(function(link) {
    link.addEventListener('click', function() {
      // Smooth scroll to section
      const targetId = this.getAttribute('href').substring(1);
      const targetElement = document.getElementById(targetId);

      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
});

// Add version warning for older docs
document.addEventListener('DOMContentLoaded', function() {
  const versionWarning = document.querySelector('.md-version');
  if (versionWarning && !versionWarning.querySelector('.version-notice')) {
    const notice = document.createElement('div');
    notice.className = 'version-notice';
    notice.innerHTML = `
      <p style="margin: 0; font-size: 0.9rem; color: #666;">
        📖 Documentation for FACET v1.0.0.
        <a href="https://github.com/rokoss21/FACET/releases">Check latest version</a>
      </p>
    `;
    versionWarning.appendChild(notice);
  }
});
