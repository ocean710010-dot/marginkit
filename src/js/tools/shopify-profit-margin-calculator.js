(function () {
  "use strict";

  var PLANS = {
    basic: { pct: 2.9, fixed: 0.30 },
    grow: { pct: 2.7, fixed: 0.30 },
    advanced: { pct: 2.5, fixed: 0.30 }
  };

  function applyPlan() {
    var plan = window.MK.val("plan", "basic");
    if (PLANS[plan]) {
      window.MK.setValue("fee_pct", PLANS[plan].pct);
      window.MK.setValue("fixed_fee", PLANS[plan].fixed.toFixed(2));
    }
  }

  function calculate() {
    var price = Math.max(0, window.MK.num("price", 0));
    var cogs = Math.max(0, window.MK.num("cogs", 0));
    var shipping = Math.max(0, window.MK.num("shipping", 0));
    var adCpa = Math.max(0, window.MK.num("ad_cpa", 0));
    var refundPct = Math.max(0, Math.min(100, window.MK.num("refund_pct", 0)));
    var feePct = Math.max(0, window.MK.num("fee_pct", 2.9));
    var fixedFee = Math.max(0, window.MK.num("fixed_fee", 0.30));

    var cardFee = price > 0 ? price * (feePct / 100) + fixedFee : 0;
    var refundReserve = price * (refundPct / 100);
    var beCpa = price - cogs - shipping - cardFee - refundReserve;
    var netProfit = beCpa - adCpa;
    var margin = price > 0 ? (netProfit / price) * 100 : 0;
    var beRoasText = beCpa > 0 && price > 0 ? (price / beCpa).toFixed(2) + "x" : "N/A";
    var actualRoasText = adCpa > 0 ? (price / adCpa).toFixed(2) + "x" : "∞";

    window.MK.setText("primary", window.MK.fmtMoney(netProfit));
    window.MK.setCardTone("primary", netProfit >= 0 ? "positive" : "negative");
    window.MK.setText("margin", window.MK.fmtPct(margin));
    window.MK.setText("be_roas", beRoasText);
    window.MK.setText("be_cpa", window.MK.fmtMoney(beCpa));

    window.MK.setBreakdown([
      ["Gross Order Revenue", window.MK.fmtMoney(price)],
      ["Product Cost (COGS)", "-" + window.MK.fmtMoney(cogs)],
      ["Fulfillment & Shipping", "-" + window.MK.fmtMoney(shipping)],
      ["Payment Fee (" + feePct.toFixed(2) + "% + $" + fixedFee.toFixed(2) + ")", "-" + window.MK.fmtMoney(cardFee)],
      ["Refund Reserve (" + refundPct.toFixed(1) + "%)", "-" + window.MK.fmtMoney(refundReserve)],
      ["Contribution Before Ads (Break-Even CPA)", window.MK.fmtMoney(beCpa)],
      ["Ad Spend / CPA (Actual ROAS: " + actualRoasText + ")", "-" + window.MK.fmtMoney(adCpa)],
      ["Net Profit per Order", window.MK.fmtMoney(netProfit)]
    ]);

    window.MK.setSummary(
      "Shopify Profit Summary\n" +
      "Price: " + window.MK.fmtMoney(price) + "\n" +
      "Net Profit: " + window.MK.fmtMoney(netProfit) + " (" + window.MK.fmtPct(margin) + ")\n" +
      "Break-Even ROAS: " + beRoasText + " | Max CPA: " + window.MK.fmtMoney(beCpa)
    );
  }

  document.addEventListener("DOMContentLoaded", function () {
    var planEl = window.MK.byId("plan");
    var pctEl = window.MK.byId("fee_pct");
    var fixedEl = window.MK.byId("fixed_fee");

    if (planEl) planEl.addEventListener("change", applyPlan);
    [pctEl, fixedEl].forEach(function (el) {
      if (el) {
        el.addEventListener("input", function () {
          if (planEl) planEl.value = "custom";
        });
      }
    });

    window.MK.bindCalculator(calculate);
  });
})();
