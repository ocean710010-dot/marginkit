(function () {
  "use strict";

  function applyCat() {
    var cat = window.MK.val("cat_preset", "15");
    if (cat !== "custom") {
      window.MK.setValue("referral_pct", cat);
    }
  }

  function calculate() {
    var price = Math.max(0, window.MK.num("price", 0));
    var landed = Math.max(0, window.MK.num("landed_cost", 0));
    var prep = Math.max(0, window.MK.num("prep_cost", 0));
    var refPct = Math.max(0, window.MK.num("referral_pct", 15));
    var fba = Math.max(0, window.MK.num("fba_fee", 0));
    var storage = Math.max(0, window.MK.num("storage_fee", 0));
    var acosPct = Math.max(0, window.MK.num("acos_pct", 0));

    var referralFee = price * (refPct / 100);
    var totalAmazonFees = referralFee + fba + storage;
    var ppcCost = price * (acosPct / 100);
    var preAdProfit = price - landed - prep - totalAmazonFees;
    var netProfit = preAdProfit - ppcCost;

    var margin = price > 0 ? (netProfit / price) * 100 : 0;
    var totalInvestment = landed + prep;
    var roi = totalInvestment > 0 ? (netProfit / totalInvestment) * 100 : 0;
    var beAcos = price > 0 ? (preAdProfit / price) * 100 : 0;

    window.MK.setText("primary", window.MK.fmtMoney(netProfit));
    window.MK.setCardTone("primary", netProfit >= 0 ? "positive" : "negative");
    window.MK.setText("margin", window.MK.fmtPct(margin));
    window.MK.setText("roi", window.MK.fmtPct(roi));
    window.MK.setText("be_acos", window.MK.fmtPct(beAcos));

    window.MK.setBreakdown([
      ["Sale Price", window.MK.fmtMoney(price)],
      ["Landed + Prep Cost", "-" + window.MK.fmtMoney(totalInvestment)],
      ["Amazon Referral Fee (" + refPct.toFixed(1) + "%)", "-" + window.MK.fmtMoney(referralFee)],
      ["FBA Fulfillment + Storage", "-" + window.MK.fmtMoney(fba + storage)],
      ["Profit Before Ads", window.MK.fmtMoney(preAdProfit)],
      ["PPC Ad Spend (" + acosPct.toFixed(1) + "%)", "-" + window.MK.fmtMoney(ppcCost)],
      ["Net Profit per Unit", window.MK.fmtMoney(netProfit)]
    ]);

    window.MK.setSummary(
      "Amazon FBA Profit Summary\n" +
      "Sale Price: " + window.MK.fmtMoney(price) + "\n" +
      "Net Profit/Unit: " + window.MK.fmtMoney(netProfit) + " (Margin: " + window.MK.fmtPct(margin) + ")\n" +
      "ROI: " + window.MK.fmtPct(roi) + " | Break-Even ACOS: " + window.MK.fmtPct(beAcos)
    );
  }

  document.addEventListener("DOMContentLoaded", function () {
    var catEl = window.MK.byId("cat_preset");
    var refEl = window.MK.byId("referral_pct");
    if (catEl) catEl.addEventListener("change", applyCat);
    if (refEl) {
      refEl.addEventListener("input", function () {
        if (catEl) catEl.value = "custom";
      });
    }
    window.MK.bindCalculator(calculate);
  });
})();
