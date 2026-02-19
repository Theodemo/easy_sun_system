"use strict";

let chart1 = null;
let chart2 = null;

function destroyCharts() {
    if (chart1 instanceof Chart) chart1.destroy();
    if (chart2 instanceof Chart) chart2.destroy();
    chart1 = null;
    chart2 = null;
}

function formatTimestamp(unixSeconds) {
    const date = new Date(unixSeconds * 1000);
    return date.toLocaleString();
}

function createChart(canvasId, data, labels, title) {
    const ctx = document.getElementById(canvasId).getContext("2d");
    const chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Valeurs",
                borderColor: "rgba(255, 210, 48, 1)",
                backgroundColor: "rgba(255, 210, 48, 0.2)",
                data: data,
                fill: false,
                pointRadius: 1,
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: "Puissance (W)", color: "#666E7A" },
                    ticks: { color: "#666E7A" },
                    grid: { color: "rgba(102, 110, 122, 0.2)" },
                },
                x: {
                    title: { display: true, text: "Temps", color: "#666E7A" },
                    ticks: { color: "#666E7A", maxTicksLimit: 10 },
                    grid: { color: "rgba(102, 110, 122, 0.2)" },
                }
            },
            plugins: {
                title: { display: true, text: title, color: "#fff" },
                legend: { display: false },
                zoom: {
                    pan: { enabled: true, mode: "x", speed: 0.1, threshold: 5 },
                    zoom: {
                        wheel: { enabled: true },
                        pinch: { enabled: true },
                        mode: "x",
                    }
                }
            }
        }
    });

    // Scroll buttons
    setupScrollButtons(chart, canvasId);
    return chart;
}

function setupScrollButtons(chart, canvasId) {
    const leftBtn = document.getElementById("moveLeft-" + canvasId);
    const rightBtn = document.getElementById("moveRight-" + canvasId);
    let scrollInterval = null;

    function scroll(direction) {
        const xScale = chart.scales["x"];
        const range = xScale.max - xScale.min;
        const step = range / 10;
        const offset = direction === "left" ? -step : step;
        xScale.options.min = xScale.min + offset;
        xScale.options.max = xScale.max + offset;
        chart.update("none");
    }

    if (leftBtn) {
        leftBtn.addEventListener("click", function () { scroll("left"); });
        leftBtn.addEventListener("mousedown", function () {
            scrollInterval = setInterval(function () { scroll("left"); }, 100);
        });
        leftBtn.addEventListener("mouseup", function () { clearInterval(scrollInterval); });
        leftBtn.addEventListener("mouseleave", function () { clearInterval(scrollInterval); });
    }

    if (rightBtn) {
        rightBtn.addEventListener("click", function () { scroll("right"); });
        rightBtn.addEventListener("mousedown", function () {
            scrollInterval = setInterval(function () { scroll("right"); }, 100);
        });
        rightBtn.addEventListener("mouseup", function () { clearInterval(scrollInterval); });
        rightBtn.addEventListener("mouseleave", function () { clearInterval(scrollInterval); });
    }
}

async function updateCharts() {
    const startDate = document.getElementById("start_date").value;
    const startTime = document.getElementById("start_time").value;
    const endDate = document.getElementById("end_date").value;
    const endTime = document.getElementById("end_time").value;

    // Convert local dates to UTC timestamps
    const startTs = Math.floor(new Date(startDate + "T" + startTime).getTime() / 1000);
    const endTs = Math.floor(new Date(endDate + "T" + endTime).getTime() / 1000);

    if (isNaN(startTs) || isNaN(endTs)) {
        alert("Dates invalides.");
        return;
    }

    try {
        const response = await fetch(
            "/api/chart-data?start_datetime=" + startTs + "&end_datetime=" + endTs
        );
        if (!response.ok) throw new Error("HTTP " + response.status);
        const data = await response.json();

        const chargwLabels = data.chargw.timestamps.map(formatTimestamp);
        const loadwLabels = data.loadw.timestamps.map(formatTimestamp);

        document.getElementById("sum-chargw").textContent = data.chargw.total_sum;
        document.getElementById("sum-loadw").textContent = data.loadw.total_sum;

        destroyCharts();
        chart1 = createChart("chart1", data.chargw.values, chargwLabels, "Production solaire (W)");
        chart2 = createChart("chart2", data.loadw.values, loadwLabels, "Consommation instantanee (W)");
    } catch (err) {
        console.error("Erreur lors du chargement des graphiques:", err);
    }
}

function initPage() {
    const now = new Date();
    const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);

    document.getElementById("start_date").value = oneDayAgo.toISOString().slice(0, 10);
    document.getElementById("start_time").value = oneDayAgo.toISOString().slice(11, 16);
    document.getElementById("end_date").value = now.toISOString().slice(0, 10);
    document.getElementById("end_time").value = now.toISOString().slice(11, 16);

    updateCharts();
}

window.addEventListener("load", initPage);
