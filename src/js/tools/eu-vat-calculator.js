(function () {
  "use strict";

  var SYMBOLS = {
    UK: "£",
    CH: "CHF ",
    NO: "NOK ",
    SE: "SEK ",
    DK: "DKK ",
    PL: "PLN ",
    CZ: "CZK ",
    HU: "HUF ",
    RO: "RON "
  };

  function getSymbol() {
    var val = window.MK.val("country", "DE:19");
    var code = val.split(":")[0];
    return SYMBOLS[code] || "€";
  }

  function applyCountry() {
    var val = window.MK.val("country", "DE:19");
    if (val !== "CUSTOM" && val.indexOf(":") !== -1) {
      var rate = val.split(":")[1];
      window.MK.setValue("rate", rate);
    }
  }

  function calculate() {
    var mode = window.MK.val("mode", "add");
    var rate = Math.max(0, window.MK.num("rate", 19));
    var amount = Math.max(0, window.MK.num("amount", 0));
    var sym = getSymbol();

    var net = 0;
    var vat = 0;
    var gross = 0;

    if (mode === "remove") {
      gross = amount;
      net = amount / (1 + rate / 100);
      vat = gross - net;
      window.MK.setLabel("primary", "Net Amount (Excl. VAT)");
      window.MK.setText("primary", window.MK.fmtMoney(net, sym));
    } else {
      net = amount;
      vat = amount * (rate / 100);
      gross = net + vat;
      window.MK.setLabel("primary", "Gross Amount (Incl. VAT)");
      window.MK.setText("primary", window.MK.fmtMoney(gross, sym));
    }

    window.MK.setText("vat", window.MK.fmtMoney(vat, sym));
    window.MK.setText("net", window.MK.fmtMoney(net, sym));
    window.MK.setText("rate_out", window.MK.fmtPct(rate));

    window.MK.setBreakdown([
      ["Net Amount (Excl. VAT)", window.MK.fmtMoney(net, sym)],
      ["VAT (" + rate.toFixed(2) + "%)", window.MK.fmtMoney(vat, sym)],
      ["Gross Amount (Incl. VAT)", window.MK.fmtMoney(gross, sym)]
    ]);

    window.MK.setSummary(
      "EU VAT Calculation (" + rate.toFixed(1) + "%)\n" +
      "Net: " + window.MK.fmtMoney(net, sym) + "\n" +
      "VAT: " + window.MK.fmtMoney(vat, sym) + "\n" +
      "Gross: " + window.MK.fmtMoney(gross, sym)
    );
  }

  document.addEventListener("DOMContentLoaded", function () {
    var countryEl = window.MK.byId("country");
    var rateEl = window.MK.byId("rate");
    if (countryEl) countryEl.addEventListener("change", applyCountry);
    if (rateEl) {
      rateEl.addEventListener("input", function () {
        if (countryEl) countryEl.value = "CUSTOM";
      });
    }
    window.MK.bindCalculator(calculate);
  });
})();
