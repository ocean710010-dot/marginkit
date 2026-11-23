(function () {
  "use strict";

  var PRESETS = {
    us_dom: { pct: 2.9, fixed: 0.30, symbol: "$" },
    us_intl: { pct: 4.4, fixed: 0.30, symbol: "$" },
    uk_dom: { pct: 1.5, fixed: 0.20, symbol: "£" },
    eu_eea: { pct: 1.5, fixed: 0.25, symbol: "€" }
  };

  function getSymbol() {
    var preset = window.MK.val("preset", "us_dom");
    return (PRESETS[preset] && PRESETS[preset].symbol) || "$";
  }

  function applyPreset() {
    var preset = window.MK.val("preset", "us_dom");
    if (PRESETS[preset]) {
      window.MK.setValue("fee_pct", PRESETS[preset].pct);
      window.MK.setValue("fixed_fee", PRESETS[preset].fixed.toFixed(2));
    }
  }

  function calculate() {
    var mode = window.MK.val("mode", "forward");
    var amount = Math.max(0, window.MK.num("amount", 0));
    var basePct = Math.max(0, window.MK.num("fee_pct", 2.9));
    var fixedFee = Math.max(0, window.MK.num("fixed_fee", 0.30));
    var fxPct = window.MK.checked("fx_conversion") ? 1.0 : 0;
    var rate = Math.min(0.95, (basePct + fxPct) / 100);
    var sym = getSymbol();

    var gross = 0;
    var fee = 0;
    var net = 0;

    if (mode === "reverse") {
      net = amount;
      gross = amount > 0 ? (amount + fixedFee) / (1 - rate) : 0;
      fee = gross - net;
      window.MK.setLabel("primary", "Recommended Invoice Amount");
      window.MK.setText("primary", window.MK.fmtMoney(gross, sym));
    } else {
      gross = amount;
      fee = amount > 0 ? gross * rate + fixedFee : 0;
      net = gross - fee;
      window.MK.setLabel("primary", "Net Payout");
      window.MK.setText("primary", window.MK.fmtMoney(net, sym));
    }

    var pctFeeAmount = gross * (basePct / 100);
    var fxFeeAmount = gross * (fxPct / 100);
    var effRate = gross > 0 ? (fee / gross) * 100 : 0;

    window.MK.setText("fee", window.MK.fmtMoney(fee, sym));
    window.MK.setText("gross", window.MK.fmtMoney(gross, sym));
    window.MK.setText("eff_rate", window.MK.fmtPct(effRate));

    window.MK.setBreakdown([
      ["Gross Charge", window.MK.fmtMoney(gross, sym)],
      ["Percentage Fee (" + basePct.toFixed(2) + "%)", "-" + window.MK.fmtMoney(pctFeeAmount, sym)],
      ["FX Conversion (" + fxPct.toFixed(2) + "%)", "-" + window.MK.fmtMoney(fxFeeAmount, sym)],
      ["Fixed Fee", "-" + window.MK.fmtMoney(amount > 0 ? fixedFee : 0, sym)],
      ["Net Payout", window.MK.fmtMoney(net, sym)]
    ]);

    window.MK.setSummary(
      "Stripe Fee Calculation (" + mode + ")\n" +
      "Gross Charge: " + window.MK.fmtMoney(gross, sym) + "\n" +
      "Total Stripe Fee: " + window.MK.fmtMoney(fee, sym) + " (" + window.MK.fmtPct(effRate) + ")\n" +
      "Net Payout: " + window.MK.fmtMoney(net, sym)
    );
  }

  document.addEventListener("DOMContentLoaded", function () {
    var presetEl = window.MK.byId("preset");
    var pctEl = window.MK.byId("fee_pct");
    var fixedEl = window.MK.byId("fixed_fee");

    if (presetEl) {
      presetEl.addEventListener("change", applyPreset);
    }
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
