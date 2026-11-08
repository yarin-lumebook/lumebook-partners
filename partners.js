/*
  LumeBook partners page: inquiry form (review prototype), shared by the he, en, ar and ru pages.
  Every visible string comes from the JSON block <script type="application/json" id="i18n"> that src/build.py writes into each page.

  What it does
  - Validates the form with inline errors, an error summary and focus handling.
  - If form[data-endpoint] is set: POSTs JSON there, shows loading, then success ONLY when the server answers 2xx with {"ok": true}, otherwise a failure state.
  - If data-endpoint is empty (today: the store has no inquiry endpoint): nothing is sent and no success is shown.
    The form prepares the message and offers the contact routes (WhatsApp, email, copy). See docs/partners/implementation-brief.md.

  Never used here: /api/ambassadors/signup or /api/recommenders/signup (they create a personal link and an account).

  Analytics: one DOM event, "lumebook:track", with {name, props}. The store wires it once to its own tracker (gt.track, behind the cookie_consent gate).
  Props are a closed list of codes. No name, contact detail or free text can pass through track().
*/
(function () {
  'use strict';

  var form = document.getElementById('partner-form');
  if (!form) return;

  var T = {};
  try { T = JSON.parse(document.getElementById('i18n').textContent); } catch (e) { return; }
  var L = T.labels || {};
  function fmt(s, vars) { return String(s).replace(/\{(\w+)\}/g, function (m, k) { return vars && vars[k] !== undefined ? vars[k] : m; }); }

  var $ = function (id) { return document.getElementById(id); };
  var fieldsBox = $('form-fields');
  var errorBox = $('form-errors');
  var resultBox = $('form-result');
  var liveBox = $('live');
  var submitBtn = $('submit-btn');
  var SUBMIT_LABEL = submitBtn.textContent;
  var descEl = $('f-desc');
  var counterEl = $('c-desc');

  function endpoint() { return (form.getAttribute('data-endpoint') || '').trim(); } // read at submit time
  var WHATSAPP = form.getAttribute('data-whatsapp') || '';
  var EMAIL = form.getAttribute('data-email') || '';
  var TIMEOUT_MS = 15000;
  var HAS_TEXT = { story: true, book: true };

  /* ---------- analytics: closed lists only ---------- */
  var ALLOWED = {
    location: ['header', 'hero_primary', 'hero_secondary', 'entry_story', 'entry_expertise', 'closing', 'closing_whatsapp',
               'handoff_whatsapp', 'handoff_email', 'handoff_copy'],
    starting_point: Object.keys(L.start || {}),
    professional_field: Object.keys(L.field || {}),
    reason: ['network', 'timeout', 'server']
  };
  function track(name, props) {
    var clean = {};
    Object.keys(props || {}).forEach(function (k) {
      if (ALLOWED[k] && ALLOWED[k].indexOf(props[k]) !== -1) clean[k] = props[k];
    });
    try { document.dispatchEvent(new CustomEvent('lumebook:track', { detail: { name: name, props: clean } })); } catch (e) { /* analytics must never break the page */ }
  }

  document.addEventListener('click', function (ev) {
    var a = ev.target.closest && ev.target.closest('[data-track]');
    if (a) track('Partner_Cta_Clicked', { location: a.getAttribute('data-track') });
    var s = ev.target.closest && ev.target.closest('[data-start]');
    if (s) {
      var radio = form.querySelector('input[name="start"][value="' + s.getAttribute('data-start') + '"]');
      if (radio) { radio.checked = true; syncConditional(); clearError('start'); }
    }
  });

  /* ---------- conditional parts ---------- */
  function val(name) {
    var el = form.elements[name];
    if (!el) return '';
    if (el.length !== undefined && !el.tagName) { // RadioNodeList
      return el.value || '';
    }
    return (el.value || '').trim();
  }
  function syncConditional() {
    $('other-wrap').hidden = val('field') !== 'other';
    $('rights-wrap').hidden = !HAS_TEXT[val('start')];
  }
  form.elements.field.addEventListener('change', function () { syncConditional(); });
  Array.prototype.forEach.call(form.elements.start, function (r) { r.addEventListener('change', syncConditional); });

  function updateCounter() { counterEl.textContent = fmt(T.counter, { n: descEl.value.length, max: descEl.maxLength }); }
  descEl.addEventListener('input', updateCounter);
  updateCounter();

  /* ---------- validation ---------- */
  var MSG = T.errors || {};
  var ERR_IDS = { fullName: 'e-name', field: 'e-field', fieldOther: 'e-other', email: 'e-email', whatsapp: 'e-wa', profile: 'e-profile',
                  start: 'e-start', rights: 'e-rights', description: 'e-desc', bookTitle: 'e-title' };
  var FOCUS_IDS = { fullName: 'f-name', field: 'f-field', fieldOther: 'f-other', email: 'f-email', whatsapp: 'f-wa', profile: 'f-profile',
                    description: 'f-desc', bookTitle: 'f-title' };

  function validate() {
    var errors = {};
    var name = val('fullName');
    if (name.length < 2 || !/\p{L}/u.test(name)) errors.fullName = MSG.fullName;
    var fld = val('field');
    if (!fld) errors.field = MSG.field;
    if (fld === 'other' && val('fieldOther').length < 2) errors.fieldOther = MSG.fieldOther;
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(val('email'))) errors.email = MSG.email;
    var wa = val('whatsapp');
    if (wa) {
      var digits = wa.replace(/\D/g, '');
      if (!/^[+\d\s().\-]+$/.test(wa) || digits.length < 9 || digits.length > 15) errors.whatsapp = MSG.whatsapp;
    }
    var prof = val('profile');
    if (prof && !(/^@[\w.]{2,30}$/.test(prof) || /^(https?:\/\/)?[^\s\/.]+(\.[^\s\/.]+)+(\/\S*)?$/i.test(prof))) errors.profile = MSG.profile;
    var start = val('start');
    if (!start) errors.start = MSG.start;
    if (HAS_TEXT[start] && !val('rights')) errors.rights = MSG.rights;
    if (val('description').length < 20) errors.description = MSG.description;
    return errors;
  }

  function fieldBox(key) { return form.querySelector('[data-field="' + key + '"]'); }
  function showError(key, text) {
    var box = fieldBox(key);
    if (!box) return;
    box.classList.add('is-invalid');
    var err = $(ERR_IDS[key]);
    if (err) err.textContent = text;
    var input = FOCUS_IDS[key] ? $(FOCUS_IDS[key]) : null;
    if (input) input.setAttribute('aria-invalid', 'true');
  }
  function clearError(key) {
    var box = fieldBox(key);
    if (!box) return;
    box.classList.remove('is-invalid');
    var err = $(ERR_IDS[key]);
    if (err) err.textContent = '';
    var input = FOCUS_IDS[key] ? $(FOCUS_IDS[key]) : null;
    if (input) input.removeAttribute('aria-invalid');
  }
  function clearAllErrors() {
    Object.keys(ERR_IDS).forEach(clearError);
    errorBox.hidden = true;
    errorBox.textContent = '';
  }
  function focusField(key) {
    var el = FOCUS_IDS[key] ? $(FOCUS_IDS[key]) : form.querySelector('[data-field="' + key + '"] input');
    if (el) { el.focus(); }
  }
  function renderSummary(errors) {
    var keys = Object.keys(errors);
    errorBox.textContent = '';
    var p = document.createElement('strong');
    p.textContent = T.summary_title;
    errorBox.appendChild(p);
    var ul = document.createElement('ul');
    keys.forEach(function (k) {
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = '#' + (FOCUS_IDS[k] || 'inquiry');
      a.textContent = errors[k];
      a.addEventListener('click', function (e) { e.preventDefault(); focusField(k); });
      li.appendChild(a);
      ul.appendChild(li);
    });
    errorBox.appendChild(ul);
    errorBox.hidden = false;
  }
  // clear a field's error as soon as it is edited
  form.addEventListener('input', function (e) {
    var box = e.target.closest && e.target.closest('[data-field]');
    if (box) clearError(box.getAttribute('data-field'));
  });
  form.addEventListener('change', function (e) {
    var box = e.target.closest && e.target.closest('[data-field]');
    if (box) clearError(box.getAttribute('data-field'));
  });

  /* ---------- payload + fallback message ---------- */
  function collect() {
    var start = val('start');
    var fld = val('field');
    var data = {
      source: 'partners_page',
      locale: T.lang || document.documentElement.lang,
      page: location.pathname,
      fullName: val('fullName'),
      field: fld,
      email: val('email'),
      startingPoint: start,
      description: val('description')
    };
    if (fld === 'other') data.fieldOther = val('fieldOther');
    if (val('whatsapp')) data.whatsapp = val('whatsapp');
    if (val('profile')) data.profile = val('profile');
    if (val('bookTitle')) data.bookTitle = val('bookTitle');
    if (HAS_TEXT[start]) data.rightsControl = val('rights'); // asked only for a written story or an existing book
    return data;
  }
  function messageText(d) {
    var lines = [T.msg_greeting, ''];
    lines.push(T.msg_name + ': ' + d.fullName);
    lines.push(T.msg_field + ': ' + (d.field === 'other' ? (T.msg_other_field + ': ' + d.fieldOther) : L.field[d.field]));
    lines.push(T.msg_start + ': ' + L.start[d.startingPoint]);
    if (d.rightsControl) lines.push(T.msg_rights + ': ' + L.rights[d.rightsControl]);
    if (d.bookTitle) lines.push(T.msg_title + ': ' + d.bookTitle);
    lines.push(T.msg_about + ': ' + d.description);
    lines.push(T.msg_email + ': ' + d.email);
    if (d.whatsapp) lines.push(T.msg_whatsapp + ': ' + d.whatsapp);
    if (d.profile) lines.push(T.msg_profile + ': ' + d.profile);
    lines.push('(' + d.locale + ')');
    return lines.join('\n');
  }

  /* ---------- result panels ---------- */
  function mk(tag, text, cls) {
    var el = document.createElement(tag);
    if (text) el.textContent = text;
    if (cls) el.className = cls;
    return el;
  }
  function showResult(kind, build) {
    resultBox.className = 'result' + (kind === 'success' ? ' is-success' : kind === 'failure' ? ' is-failure' : '');
    resultBox.textContent = '';
    resultBox.setAttribute('role', kind === 'failure' ? 'alert' : 'status');
    build(resultBox);
    fieldsBox.hidden = true;
    errorBox.hidden = true;
    resultBox.hidden = false;
    resultBox.focus();
  }
  function backToForm(reset) {
    resultBox.hidden = true;
    resultBox.textContent = '';
    if (reset) { form.reset(); syncConditional(); updateCounter(); }
    fieldsBox.hidden = false;
    var first = $('f-name');
    if (first) first.focus();
  }
  function routeButtons(box, text) {
    var row = mk('div', '', 'row');
    var wa = mk('a', T.btn_whatsapp, 'btn');
    wa.href = 'https://wa.me/' + WHATSAPP + '?text=' + encodeURIComponent(text);
    wa.target = '_blank'; wa.rel = 'noopener';
    wa.addEventListener('click', function () { track('Partner_Cta_Clicked', { location: 'handoff_whatsapp' }); });
    var mail = mk('a', T.btn_email, 'btn btn-ghost');
    mail.href = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent(T.msg_subject) + '&body=' + encodeURIComponent(text);
    mail.addEventListener('click', function () { track('Partner_Cta_Clicked', { location: 'handoff_email' }); });
    row.appendChild(wa); row.appendChild(mail);
    return row;
  }
  function showHandoff(d) {
    var text = messageText(d);
    showResult('handoff', function (box) {
      box.appendChild(mk('h3', T.handoff_title));
      box.appendChild(mk('p', T.handoff_text));
      var previewEl = mk('div', text, 'preview');
      box.appendChild(previewEl);
      var row = routeButtons(box, text);
      var copy = mk('button', T.btn_copy, 'btn btn-ghost');
      copy.type = 'button';
      var status = mk('p', '', 'copy-status');
      status.setAttribute('role', 'status');
      copy.addEventListener('click', function () {
        track('Partner_Cta_Clicked', { location: 'handoff_copy' });
        var done = function () { status.textContent = T.copied; };
        var fail = function () {
          try { var rg = document.createRange(); rg.selectNodeContents(previewEl); var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(rg); } catch (e) { /* selection is a convenience only */ }
          status.textContent = T.copy_fail;
          status.style.color = 'var(--am-danger)';
        };
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, fail); else fail();
      });
      var edit = mk('button', T.btn_edit, 'btn btn-ghost');
      edit.type = 'button';
      edit.addEventListener('click', function () { backToForm(false); });
      row.appendChild(copy); row.appendChild(edit);
      box.appendChild(row);
      box.appendChild(status);
    });
    liveBox.textContent = T.handoff_live;
  }
  function showSuccess() {
    showResult('success', function (box) {
      box.appendChild(mk('h3', T.success_title));
      box.appendChild(mk('p', T.success_text));
      var row = mk('div', '', 'row');
      var again = mk('button', T.btn_again, 'btn btn-ghost');
      again.type = 'button';
      again.addEventListener('click', function () { backToForm(true); });
      row.appendChild(again);
      box.appendChild(row);
    });
    liveBox.textContent = T.success_live;
  }
  function showFailure(d) {
    var text = messageText(d);
    showResult('failure', function (box) {
      box.appendChild(mk('h3', T.failure_title));
      box.appendChild(mk('p', T.failure_text));
      var row = routeButtons(box, text);
      var retry = mk('button', T.btn_retry, 'btn btn-ghost');
      retry.type = 'button';
      retry.addEventListener('click', function () { backToForm(false); });
      row.appendChild(retry);
      box.appendChild(row);
    });
    liveBox.textContent = T.failure_live;
  }

  /* ---------- submit ---------- */
  var sending = false;
  function setSending(on) {
    sending = on;
    submitBtn.disabled = on;
    submitBtn.setAttribute('aria-busy', on ? 'true' : 'false');
    form.setAttribute('aria-busy', on ? 'true' : 'false');
    submitBtn.textContent = '';
    if (on) { submitBtn.appendChild(mk('span', '', 'spinner')); submitBtn.appendChild(document.createTextNode(T.sending)); }
    else submitBtn.textContent = SUBMIT_LABEL;
    if (on) liveBox.textContent = T.sending_live;
  }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    if (sending) return;
    if ($('f-company').value) return; // honeypot: a bot filled the hidden field

    clearAllErrors();
    var errors = validate();
    var keys = Object.keys(errors);
    if (keys.length) {
      keys.forEach(function (k) { showError(k, errors[k]); });
      renderSummary(errors);
      errorBox.focus();
      liveBox.textContent = fmt(T.summary_live, { n: keys.length });
      return;
    }

    var data = collect();
    var url = endpoint();
    if (!url) { showHandoff(data); return; }

    setSending(true);
    var ctl = typeof AbortController === 'function' ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctl) ctl.abort(); }, TIMEOUT_MS);
    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify(data),
      signal: ctl ? ctl.signal : undefined
    }).then(function (res) {
      clearTimeout(timer);
      var parse = res.ok ? res.json().catch(function () { return null; }) : Promise.resolve(null);
      return parse.then(function (body) { return { ok: res.ok && body && body.ok === true }; });
    }).catch(function (err) {
      clearTimeout(timer);
      return { ok: false, reason: err && err.name === 'AbortError' ? 'timeout' : 'network' };
    }).then(function (r) {
      setSending(false);
      if (r.ok) {
        track('Partner_Inquiry_Submitted', { starting_point: data.startingPoint, professional_field: data.field });
        showSuccess();
      } else {
        track('Partner_Inquiry_Failed', { reason: r.reason || 'server' });
        showFailure(data);
      }
    });
  });

  syncConditional();
})();
