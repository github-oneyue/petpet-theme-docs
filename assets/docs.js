// Documentation site behaviour: mobile contents toggle, active TOC entry,
// and a copy button on code blocks. No dependencies, no bundler.

(function () {
  var toggle = document.getElementById('navToggle');
  var body = document.body;

  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = body.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    // Close the mobile contents panel after picking a page in it.
    document.querySelectorAll('.sidebar a').forEach(function (link) {
      link.addEventListener('click', function () {
        body.classList.remove('nav-open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // Highlight the TOC entry for the section currently in view.
  var tocLinks = Array.prototype.slice.call(
    document.querySelectorAll('.toc a[href^="#"]')
  );

  if (tocLinks.length && 'IntersectionObserver' in window) {
    var byId = {};
    var targets = [];

    tocLinks.forEach(function (link) {
      var id = decodeURIComponent(link.getAttribute('href').slice(1));
      var el = document.getElementById(id);
      if (el) {
        byId[id] = link;
        targets.push(el);
      }
    });

    var visible = new Set();

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) visible.add(entry.target.id);
          else visible.delete(entry.target.id);
        });

        var firstId = null;
        for (var i = 0; i < targets.length; i += 1) {
          if (visible.has(targets[i].id)) { firstId = targets[i].id; break; }
        }

        tocLinks.forEach(function (link) { link.classList.remove('is-active'); });
        if (firstId && byId[firstId]) byId[firstId].classList.add('is-active');
      },
      { rootMargin: '-72px 0px -70% 0px', threshold: 0 }
    );

    targets.forEach(function (el) { observer.observe(el); });
  }

  // Copy-to-clipboard on commands only; plain text snippets stay selectable.
  document.querySelectorAll('pre').forEach(function (pre) {
    var code = pre.querySelector('code');
    if (!code) return;

    var button = document.createElement('button');
    button.type = 'button';
    button.textContent = 'Copy';
    button.setAttribute('aria-label', 'Copy code');
    Object.assign(button.style, {
      position: 'absolute',
      top: '8px',
      right: '8px',
      padding: '4px 9px',
      font: '500 10px/1 "DM Mono", monospace',
      letterSpacing: '.1em',
      textTransform: 'uppercase',
      color: 'rgba(255,255,255,.62)',
      background: 'rgba(255,255,255,.08)',
      border: '1px solid rgba(255,255,255,.18)',
      borderRadius: '2px',
      cursor: 'pointer',
      opacity: '0',
      transition: 'opacity .18s ease'
    });

    Object.assign(pre.style, { position: 'relative' });
    pre.appendChild(button);

    pre.addEventListener('mouseenter', function () { button.style.opacity = '1'; });
    pre.addEventListener('mouseleave', function () { button.style.opacity = '0'; });
    button.addEventListener('focus', function () { button.style.opacity = '1'; });

    button.addEventListener('click', function () {
      var text = code.innerText;
      var done = function () {
        button.textContent = 'Copied';
        setTimeout(function () { button.textContent = 'Copy'; }, 1400);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () {});
      } else {
        var area = document.createElement('textarea');
        area.value = text;
        document.body.appendChild(area);
        area.select();
        try { document.execCommand('copy'); done(); } catch (e) {}
        document.body.removeChild(area);
      }
    });
  });
})();
