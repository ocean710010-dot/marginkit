(function () {
  "use strict";

  var PRESETS = {
    us_std: { pct: 3.49, fixed: 0.49 },
    us_inv: { pct: 2.99, fixed: 0.49 },
    micro: { pct: 4.99, fixed: 0.09 }
  };

  function applyPreset() {
    var preset = window.MK.val("preset", "us_std");
    if (PRESETS[preset]) {
      window.MK.setValue("fee_pct", PRESETS[preset].pct);
      window.MK.setValue("fixed_fee", PRESETS[preset].fixed.toFixed(2));
    }
  }

  function calculate() {
    var mode = window.MK.val("mode", "forward");
    var amount = Math.max(0, window.MK.num("amount", 0));
    var basePct = Math.max(0, window.MK.num("fee_pct", 3.49));
    var fixedFee = Math.max(0, window.MK.num("fixed_fee", 0.49));
    var intlPct = window.MK.checked("intl") ? 1.5 : 0;
    var fxPct = Math.max(0, window.MK.num("fx_pct", 0));

    var rate = Math.min(0.95, (basePct + intlPct + fxPct) / 100);
    var gross = 0;
    var fee = 0;
    var net = 0;

    if (mode === "reverse") {
      net = amount;
      gross = amount > 0 ? (amount + fixedFee) / (1 - rate) : 0;
      fee = gross - net;
      window.MK.setLabel("primary", "Recommended Invoice Total");
      window.MK.setText("primary", window.MK.fmtMoney(gross));
    } else {
      gross = amount;
      fee = amount > 0 ? gross * rate + fixedFee : 0;
      net = gross - fee;
      window.MK.setLabel("primary", "Net Payout");
      window.MK.setText("primary", window.MK.fmtMoney(net));
    }

    var effRate = gross > 0 ? (fee / gross) * 100 : 0;

    window.MK.setText("fee", window.MK.fmtMoney(fee));
    window.MK.setText("gross", window.MK.fmtMoney(gross));
    window.MK.setText("eff_rate", window.MK.fmtPct(effRate));

    window.MK.setBreakdown([
      ["Gross Invoice", window.MK.fmtMoney(gross)],
      ["Base Fee (" + basePct.toFixed(2) + "%)", "-" + window.MK.fmtMoney(gross * (basePct / 100))],
      ["Cross-Border (" + intlPct.toFixed(2) + "%)", "-" + window.MK.fmtMoney(gross * (intlPct / 100))],
      ["FX Spread (" + fxPct.toFixed(2) + "%)", "-" + window.MK.fmtMoney(gross * (fxPct / 100))],
      ["Fixed Fee", "-" + window.MK.fmtMoney(amount > 0 ? fixedFee : 0)],
      ["Net Payout", window.MK.fmtMoney(net)]
    ]);

    window.MK.setSummary(
      "PayPal Fee Calculation (" + mode + ")\n" +
      "Gross: " + window.MK.fmtMoney(gross) + "\n" +
      "Total Fee: " + window.MK.fmtMoney(fee) + " (" + window.MK.fmtPct(effRate) + ")\n" +
      "Net Payout: " + window.MK.fmtMoney(net)
    );
  }

  document.addEventListener("DOMContentLoaded", function () {
    var presetEl = window.MK.byId("preset");
    var pctEl = window.MK.byId("fee_pct");
    var fixedEl = window.MK.byId("fixed_fee");

    if (presetEl) presetEl.addEventListener("change", applyPreset);
    [pctEl, fixedEl].forEach(function (el) {
      if (el) {
        el.addEventListener("input", function () {
          if (presetEl) presetEl.value = "custom";
        });
      }
    });

    window.MK.bindCalculator(calculate);
  });
})();
