(function () {
  "use strict";

  function renderChart(series) {
    var box = window.MK.byId("mk-chart");
    if (!box || !series.length) return;
    box.hidden = false;

    var w = 480;
    var h = 150;
    var padX = 14;
    var padY = 16;
    var maxVal = Math.max.apply(null, series.concat([1]));
    var minVal = Math.min.apply(null, series);
    var span = Math.max(1, maxVal - minVal);

    var pts = series.map(function (v, idx) {
      var x = padX + (idx / (series.length - 1)) * (w - padX * 2);
      var y = h - padY - ((v - minVal) / span) * (h - padY * 2);
      return x.toFixed(1) + "," + y.toFixed(1);
    });

    var areaPts = pts.concat([
      (w - padX).toFixed(1) + "," + (h - padY).toFixed(1),
      padX.toFixed(1) + "," + (h - padY).toFixed(1)
    ]);

    box.innerHTML =
      '<div class="kpi-label" style="margin-bottom:6px;">12-Month MRR Trajectory</div>' +
      '<svg viewBox="0 0 ' + w + " " + h + '" role="img" aria-label="12-month MRR trajectory chart">' +
      '<polygon points="' + areaPts.join(" ") + '" fill="rgba(37, 99, 235, 0.12)"></polygon>' +
      '<polyline fill="none" stroke="#2563eb" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" points="' + pts.join(" ") + '"></polyline>' +
      "</svg>";
  }

  function calculate() {
    var startMrr = Math.max(0, window.MK.num("mrr", 0));
    var newMrr = Math.max(0, window.MK.num("new_mrr", 0));
    var churnPct = Math.max(0, Math.min(100, window.MK.num("churn_pct", 0)));
    var expPct = Math.max(0, Math.min(100, window.MK.num("expansion_pct", 0)));
    var arpu = Math.max(1, window.MK.num("arpu", 99));

    var monthlyFactor = Math.max(0, 1 - churnPct / 100 + expPct / 100);
    var series = [startMrr];
    var cur = startMrr;
    for (var m = 1; m <= 12; m++) {
      cur = Math.max(0, cur * monthlyFactor + newMrr);
      series.push(cur);
    }

    var mrr12 = series[12];
    var arr12 = mrr12 * 12;
    var ndr12 = Math.pow(monthlyFactor, 12) * 100;
    var ltv = churnPct > 0 ? arpu / (churnPct / 100) : arpu * 60;
    var netChurn = churnPct - expPct;
    var ceiling = netChurn > 0 ? newMrr / (netChurn / 100) : Infinity;

    window.MK.setText("primary", window.MK.fmtMoney(mrr12));
    window.MK.setText("arr12", window.MK.fmtMoney(arr12));
    window.MK.setText("ndr", window.MK.fmtPct(ndr12));
    window.MK.setText("ltv", window.MK.fmtMoney(ltv));

    window.MK.setBreakdown([
      ["Starting MRR (Month 0)", window.MK.fmtMoney(startMrr)],
      ["Month 3 Projected MRR", window.MK.fmtMoney(series[3])],
      ["Month 6 Projected MRR", window.MK.fmtMoney(series[6])],
      ["Month 9 Projected MRR", window.MK.fmtMoney(series[9])],
      ["Month 12 Projected MRR", window.MK.fmtMoney(mrr12)],
      ["Net Monthly Revenue Churn", window.MK.fmtPct(netChurn)],
      ["Implied MRR Ceiling", Number.isFinite(ceiling) ? window.MK.fmtMoney(ceiling) : "Uncapped (NDR ≥ 100%)"]
    ]);

    renderChart(series);

    window.MK.setSummary(
      "SaaS MRR Forecast\n" +
      "Start MRR: " + window.MK.fmtMoney(startMrr) + " -> Month 12 MRR: " + window.MK.fmtMoney(mrr12) + "\n" +
      "Month 12 ARR: " + window.MK.fmtMoney(arr12) + " | NDR: " + window.MK.fmtPct(ndr12) + " | LTV: " + window.MK.fmtMoney(ltv)
    );
  }

  document.addEventListener("DOMContentLoaded", function () {
    window.MK.bindCalculator(calculate);
  });
})();
