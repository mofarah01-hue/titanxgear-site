// Waitlist forms (hero and bottom of page).
//
// DESTINATION is 'preview' until Mo picks where emails go. In preview nothing leaves the browser:
// the form validates, then says plainly that nothing was sent. See README.md, "Waitlist".
(() => {
  const DESTINATION = 'preview'; // 'preview' | 'supabase' | 'formspree'
  const CONFIG = {
    // Filled in only after Mo picks. The Supabase anon key is public by design; the table's
    // row-level security must allow insert only (no select), so the list cannot be read from the site.
    supabase: { url: '', anonKey: '', table: 'waitlist' },
    formspree: { endpoint: '' },
  };

  const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  // Decide what one waitlist entry contains. `form` is the submitted <form>; `email` is already trimmed
  // and checked. The bottom form has a role choice (coach, athlete, parent, other); the hero form has none.
  function buildEntry(form, email) {
    // TODO(human): choose the fields each entry carries, then return them as one plain object.
    return { email };
  }

  async function send(entry) {
    if (DESTINATION === 'preview') return { ok: true, preview: true };
    if (DESTINATION === 'supabase') {
      const { url, anonKey, table } = CONFIG.supabase;
      if (!url || !anonKey) throw new Error('Supabase destination chosen but url or anonKey is empty');
      const res = await fetch(`${url}/rest/v1/${table}`, {
        method: 'POST',
        headers: { apikey: anonKey, Authorization: `Bearer ${anonKey}`, 'Content-Type': 'application/json', Prefer: 'return=minimal' },
        body: JSON.stringify(entry),
      });
      // 409 means this email is already on the list: treat it as success, say nothing different.
      if (res.ok || res.status === 409) return { ok: true };
      throw new Error(`Supabase answered ${res.status}`);
    }
    if (DESTINATION === 'formspree') {
      const { endpoint } = CONFIG.formspree;
      if (!endpoint) throw new Error('Formspree destination chosen but endpoint is empty');
      const res = await fetch(endpoint, { method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' }, body: JSON.stringify(entry) });
      if (res.ok) return { ok: true };
      throw new Error(`Formspree answered ${res.status}`);
    }
    throw new Error(`Unknown waitlist destination "${DESTINATION}"`);
  }

  function say(form, text, kind) {
    const msg = form.querySelector('.wl-msg');
    msg.textContent = text;
    msg.className = `wl-msg ${kind || ''}`;
  }

  document.querySelectorAll('form[data-waitlist]').forEach((form) => {
    const input = form.querySelector('input[type="email"]');
    const button = form.querySelector('button[type="submit"]');
    input.addEventListener('input', () => input.removeAttribute('aria-invalid'));

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = input.value.trim();
      if (!EMAIL.test(email)) {
        input.setAttribute('aria-invalid', 'true');
        say(form, 'Enter an email address like name@club.com.', 'err');
        input.focus();
        return;
      }
      button.disabled = true;
      try {
        const result = await send(buildEntry(form, email));
        if (result.preview) {
          say(form, 'Preview only: nothing was sent. The waitlist opens once its destination is chosen.', 'ok');
        } else {
          say(form, "You're on the list. We'll email you when Titan X is ready.", 'ok');
          form.reset();
        }
      } catch (err) {
        console.error('[titanx] waitlist send failed:', err); // watchdog: never swallow the reason
        say(form, 'That did not go through. Check your connection and try again.', 'err');
      } finally {
        button.disabled = false;
      }
    });
  });
})();
