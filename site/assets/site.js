// Atmos Design + Build. No dependencies.
(() => {
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  // Analytics hook: fires into GA4 (dataLayer) or Plausible if either is installed. See docs/LAUNCH.md.
  const track = (name) => {
    if (window.dataLayer) window.dataLayer.push({ event: name });
    if (window.plausible) window.plausible(name);
  };
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href^="tel:"], a[href^="mailto:"]');
    if (a) track(a.protocol === 'tel:' ? 'click_to_call' : 'email_click');
  });

  // Navigation: mobile panel + dropdowns
  const nav = document.getElementById('nav');
  const burger = document.querySelector('.hdr__burger');
  const drops = $$('.nav__drop');
  const hover = matchMedia('(hover: hover) and (min-width: 1021px)');
  const setDrop = (d, open) => d.firstElementChild.setAttribute('aria-expanded', open);
  const setNav = (open) => {
    nav.classList.toggle('is-open', open);
    document.body.classList.toggle('nav-open', open);
    burger.setAttribute('aria-expanded', open);
    burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  };
  burger.addEventListener('click', () => setNav(!nav.classList.contains('is-open')));
  drops.forEach((d) => {
    const b = d.firstElementChild;
    b.addEventListener('click', () => {
      const open = hover.matches || b.getAttribute('aria-expanded') !== 'true';
      drops.forEach((x) => setDrop(x, x === d && open));
    });
    d.addEventListener('mouseenter', () => hover.matches && drops.forEach((x) => setDrop(x, x === d)));
    d.addEventListener('mouseleave', () => hover.matches && setDrop(d, false));
    d.addEventListener('focusout', (e) => hover.matches && !d.contains(e.relatedTarget) && setDrop(d, false));
  });
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.nav__drop')) drops.forEach((d) => setDrop(d, false));
  });
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    const open = drops.find((d) => d.contains(document.activeElement));
    drops.forEach((d) => setDrop(d, false));
    if (open) open.firstElementChild.focus();
    if (nav.classList.contains('is-open')) { setNav(false); burger.focus(); }
  });
  const here = location.pathname.replace(/\/$/, '') || '/';
  $$('.nav a, .ftr__nav a').forEach((a) => {
    if (a.getAttribute('href') === here) a.setAttribute('aria-current', 'page');
  });

  // Scroll reveal
  const revealables = $$('.shead, .aud__card, .pcard, .step, .fcard, .scope > div, .split, .boards figure, .gallery figure, .quote, .compare, .stats li, .faqs, .form, .bid__intro');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => entries.forEach((en) => {
      if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
    }), { rootMargin: '0px 0px -8% 0px' });
    revealables.forEach((el) => { el.classList.add('reveal'); io.observe(el); });
  }

  // Hide the sticky mobile bar while the bid form is on screen
  const bid = document.getElementById('bid');
  if (bid && 'IntersectionObserver' in window) {
    new IntersectionObserver(([en]) => document.body.classList.toggle('at-bid', en.isIntersecting), { rootMargin: '-30% 0px 0px 0px' }).observe(bid);
  }

  // Before/after slider
  $$('.compare input').forEach((input) => input.addEventListener('input', () => {
    input.parentElement.style.setProperty('--pos', input.value + '%');
  }));

  // Portfolio filters
  $$('.filters').forEach((f) => f.addEventListener('click', (e) => {
    const b = e.target.closest('button');
    if (!b) return;
    $$('button', f).forEach((x) => x.setAttribute('aria-pressed', x === b));
    $$('.pcard').forEach((c) => { c.hidden = b.dataset.cat !== 'all' && c.dataset.cat !== b.dataset.cat; });
  }));

  // Bid form: two steps, submitted to Netlify Forms without leaving the page
  const TYPE_BY_PAGE = {
    '/property-managers': 'Apartment community',
    '/multifamily-renovation': 'Apartment community',
    '/hotel-renovation': 'Hotel / hospitality',
    '/short-term-rental-renovation': 'Short-term rental',
  };
  const params = new URLSearchParams(location.search);
  $$('form.form').forEach((form) => {
    const steps = $$('.form__step', form);
    const dots = $$('.form__steps li', form);
    const error = form.querySelector('.form__error');
    const show = (i) => {
      steps.forEach((s, j) => s.classList.toggle('is-on', i === j));
      dots.forEach((d, j) => d.classList.toggle('is-on', j <= i));
    };
    const firstInvalid = (step) => {
      const bad = $$('input, select, textarea', step).filter((f) => {
        const ok = f.checkValidity();
        if (ok) f.removeAttribute('aria-invalid'); else f.setAttribute('aria-invalid', 'true');
        return !ok;
      });
      return bad[0];
    };
    const next = () => {
      const bad = firstInvalid(steps[0]);
      if (bad) { bad.reportValidity(); return; }
      show(1);
      form.scrollIntoView({ block: 'start' });
      steps[1].querySelector('input').focus({ preventScroll: true });
      track('bid_form_step_2');
    };
    form.noValidate = true;
    form.elements.page.value = location.pathname;
    if (TYPE_BY_PAGE[here]) form.elements['property-type'].value = TYPE_BY_PAGE[here];
    if (params.get('scope') === 'handyman') form.querySelector('[value*="handyman"]').checked = true;
    if (params.has('packet')) form.elements['vendor-packet'].checked = true;
    if (params.has('walk')) form.elements.message.value = "I'd like to schedule a property walk.";
    show(0);
    form.querySelector('.form__next').addEventListener('click', next);
    form.querySelector('.form__back').addEventListener('click', () => show(0));
    form.addEventListener('input', (e) => e.target.removeAttribute('aria-invalid'));
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!steps[1].classList.contains('is-on')) { next(); return; }
      const btn = form.querySelector('[type=submit]');
      btn.disabled = true;
      error.hidden = true;
      try {
        const res = await fetch('/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams(new FormData(form)).toString(),
        });
        if (!res.ok) throw new Error(res.status);
        track('generate_lead');
        location.href = '/thank-you';
      } catch (err) {
        error.hidden = false;
        btn.disabled = false;
      }
    });
  });
})();
