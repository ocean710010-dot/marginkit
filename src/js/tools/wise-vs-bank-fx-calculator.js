(function () {
  "use strict";

  function calculate() {
    var amount = Math.max(0, window.MK.num("amount", 0));
    var txYr = Math.max(1, window.MK.num("transfers_yr", 1));
    var bankWire = Math.max(0, window.MK.num("bank_wire", 0));
    var bankMarkupPct = Math.max(0, window.MK.num("bank_markup", 3.5));
    var fxPct = Math.max(0, window.MK.num("fx_fee_pct", 0.45));

    var bankSpreadCost = amount * (bankMarkupPct / 100);
    var bankCost = amount > 0 ? bankWire + bankSpreadCost : 0;
    var fxCost = amount * (fxPct / 100);
    var saveTx = bankCost - fxCost;
    var saveYr = saveTx * txYr;
    var pctSaved = amount > 0 ? (saveTx / amount) * 100 : 0;

    window.MK.setText("primary", window.MK.fmtMoney(saveYr));
    window.MK.setCardTone("primary", saveYr >= 0 ? "positive" : "negative");
    window.MK.setText("save_tx", window.MK.fmtMoney(saveTx));
    window.MK.setText("bank_cost", window.MK.fmtMoney(bankCost));
    window.MK.setText("fx_cost", window.MK.fmtMoney(fxCost));

    window.MK.setBreakdown([
      ["Transfer Principal", window.MK.fmtMoney(amount)],
      ["Bank Explicit Wire Fee", window.MK.fmtMoney(amount > 0 ? bankWire : 0)],
      ["Bank Hidden FX Spread (" + bankMarkupPct.toFixed(2) + "%)", window.MK.fmtMoney(bankSpreadCost)],
      ["Bank Total Cost / Transfer", window.MK.fmtMoney(bankCost)],
      ["Mid-Market FX Provider (" + fxPct.toFixed(2) + "%)", window.MK.fmtMoney(fxCost)],
      ["Savings per Transfer (" + window.MK.fmtPct(pctSaved) + ")", window.MK.fmtMoney(saveTx)],
      ["Annual Savings (" + Math.round(txYr) + " transfers/yr)", window.MK.fmtMoney(saveYr)]
    ]);

    window.MK.setSummary(
      "Cross-Border FX Savings\n" +
      "Transfer: " + window.MK.fmtMoney(amount) + " x " + Math.round(txYr) + "/yr\n" +
      "Bank Cost: " + window.MK.fmtMoney(bankCost) + " vs FX Provider: " + window.MK.fmtMoney(fxCost) + "\n" +
      "Annual Savings: " + window.MK.fmtMoney(saveYr)
    );
  }

  document.addEventListener("DOMContentLoaded", function () {
    window.MK.bindCalculator(calculate);
  });
})();
