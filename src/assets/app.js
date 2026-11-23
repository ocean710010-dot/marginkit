(function () {
  "use strict";

  function byId(id) {
    return document.getElementById(id);
  }

  function num(id, fallback) {
    if (fallback === undefined) fallback = 0;
    var el = byId(id);
    if (!el) return fallback;
    var v = parseFloat(el.value);
    return Number.isFinite(v) ? v : fallback;
  }

  function val(id, fallback) {
    if (fallback === undefined) fallback = "";
    var el = byId(id);
    return el ? el.value : fallback;
  }

  function checked(id) {
    var el = byId(id);
    return Boolean(el && el.checked);
  }

  function setValue(id, value) {
    var el = byId(id);
    if (el) el.value = value;
  }

  function setText(id, text) {
    var el = byId("out-" + id);
    if (el) el.textContent = text;
  }

  function setLabel(id, text) {
    var el = document.querySelector('[data-output-label="' + id + '"]');
    if (el) el.textContent = text;
  }

  function setCardTone(id, tone) {
    var card = document.querySelector('[data-output-card="' + id + '"]');
    if (!card) return;
    card.classList.remove("positive", "negative");
    if (tone === "positive" || tone === "negative") {
      card.classList.add(tone);
    }
  }

  function fmtMoney(n, symbol, decimals) {
    if (symbol === undefined) symbol = "$";
    if (decimals === undefined) decimals = 2;
    if (!Number.isFinite(n)) return symbol + "0.00";
    var sign = n < 0 ? "-" : "";
    var absVal = Math.abs(n);
    var formatted = absVal.toLocaleString("en-US", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
    return sign + symbol + formatted;
  }

  function fmtPct(n, decimals) {
    if (decimals === undefined) decimals = 2;
    if (!Number.isFinite(n)) return "0.00%";
    return n.toFixed(decimals) + "%";
  }

  function setBreakdown(rows) {
    var tbody = byId("mk-breakdown-body");
    if (!tbody) return;
    tbody.innerHTML = "";
    rows.forEach(function (row) {
      var tr = document.createElement("tr");
      var tdLabel = document.createElement("td");
      tdLabel.textContent = row[0];
      var tdVal = document.createElement("td");
      tdVal.textContent = row[1];
      tr.appendChild(tdLabel);
      tr.appendChild(tdVal);
      tbody.appendChild(tr);
    });
  }

  var currentSummary = "";

  function setSummary(text) {
    currentSummary = text || "";
  }

  function bindCalculator(calcFn) {
    var form = byId("mk-calc-form");
    if (!form) return;

    var run = function () {
      calcFn();
    };

    form.addEventListener("input", run);
    form.addEventListener("change", run);

    var resetBtn = byId("mk-reset-btn");
    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        form.reset();
        run();
      });
    }

    var copyBtn = byId("mk-copy-btn");
    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        if (!currentSummary) return;
        var finish = function () {
          var prev = copyBtn.textContent;
          copyBtn.textContent = "Copied!";
          setTimeout(function () {
            copyBtn.textContent = prev;
          }, 1600);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(currentSummary).then(finish).catch(finish);
        } else {
          finish();
        }
      });
    }

    run();
  }

  function initDirectory() {
    var grid = byId("mk-tools-grid");
    if (!grid) return;

    var searchInput = byId("mk-search");
    var pills = Array.prototype.slice.call(document.querySelectorAll("[data-filter]"));
    var cards = Array.prototype.slice.call(grid.querySelectorAll(".tool-card"));
    var empty = byId("mk-empty");
    var activeCat = "all";

    function applyFilter() {
      var q = searchInput ? searchInput.value.trim().toLowerCase() : "";
      var visible = 0;
      cards.forEach(function (card) {
        var cat = card.getAttribute("data-category") || "";
        var text = (card.getAttribute("data-search") || "").toLowerCase();
        var okCat = activeCat === "all" || cat === activeCat;
        var okSearch = !q || text.indexOf(q) !== -1;
        var show = okCat && okSearch;
        card.style.display = show ? "" : "none";
        if (show) visible++;
      });
      if (empty) {
        empty.style.display = visible === 0 ? "block" : "none";
      }
    }

    pills.forEach(function (pill) {
      pill.addEventListener("click", function () {
        activeCat = pill.getAttribute("data-filter") || "all";
        pills.forEach(function (p) {
          p.classList.toggle("active", p === pill);
        });
        applyFilter();
      });
    });

    if (searchInput) {
      searchInput.addEventListener("input", applyFilter);
    }
  }

  window.MK = {
    byId: byId,
    num: num,
    val: val,
    checked: checked,
    setValue: setValue,
    setText: setText,
    setLabel: setLabel,
    setCardTone: setCardTone,
    fmtMoney: fmtMoney,
    fmtPct: fmtPct,
    setBreakdown: setBreakdown,
    setSummary: setSummary,
    bindCalculator: bindCalculator,
  };

  document.addEventListener("DOMContentLoaded", initDirectory);
})();
