(function () {
  "use strict";

  function calculate() {
    var targetNet = Math.max(0, window.MK.num("target_net", 0));
    var taxPct = Math.max(0, Math.min(80, window.MK.num("tax_pct", 28)));
    var overhead = Math.max(0, window.MK.num("overhead", 0));
    var weeksOff = Math.max(0, Math.min(51, window.MK.num("weeks_off", 4)));
    var hoursWeek = Math.max(1, window.MK.num("hours_week", 40));
    var billablePct = Math.max(5, Math.min(100, window.MK.num("billable_pct", 65)));

    var preTaxIncome = targetNet / (1 - taxPct / 100);
    var taxAmount = preTaxIncome - targetNet;
    var reqGross = preTaxIncome + overhead;

    var workingWeeks = Math.max(1, 52 - weeksOff);
    var billableHours = workingWeeks * hoursWeek * (billablePct / 100);
    var hourlyRate = billableHours > 0 ? reqGross / billableHours : 0;
    var dayRate = hourlyRate * 8;
    var monthlyRev = reqGross / 12;

    window.MK.setText("primary", window.MK.fmtMoney(hourlyRate));
    window.MK.setText("day_rate", window.MK.fmtMoney(dayRate));
    window.MK.setText("req_gross", window.MK.fmtMoney(reqGross));
    window.MK.setText("monthly_rev", window.MK.fmtMoney(monthlyRev));

    window.MK.setBreakdown([
      ["Target Take-Home Net", window.MK.fmtMoney(targetNet)],
      ["Estimated Income & SE Taxes (" + taxPct.toFixed(1) + "%)", window.MK.fmtMoney(taxAmount)],
      ["Annual Business Overhead", window.MK.fmtMoney(overhead)],
      ["Required Annual Gross Revenue", window.MK.fmtMoney(reqGross)],
      ["Working Weeks / Year", workingWeeks + " weeks"],
      ["Total Billable Hours / Year", Math.round(billableHours).toLocaleString("en-US") + " hrs"],
      ["Minimum Hourly Rate", window.MK.fmtMoney(hourlyRate)],
      ["Recommended 8-Hour Day Rate", window.MK.fmtMoney(dayRate)]
    ]);

    window.MK.setSummary(
      "Freelance Rate Plan\n" +
      "Hourly Rate: " + window.MK.fmtMoney(hourlyRate) + "/hr | Day Rate: " + window.MK.fmtMoney(dayRate) + "/day\n" +
      "Required Gross: " + window.MK.fmtMoney(reqGross) + "/yr (" + Math.round(billableHours) + " billable hrs)"
    );
  }

  document.addEventListener("DOMContentLoaded", function () {
    window.MK.bindCalculator(calculate);
  });
})();
