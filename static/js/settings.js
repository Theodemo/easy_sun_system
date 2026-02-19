"use strict";

function showAlert(message, type) {
    const el = document.getElementById("alert");
    el.textContent = message;
    el.className = "alert alert--" + type;
    el.style.display = "block";
    setTimeout(function () { el.style.display = "none"; }, 5000);
}

async function configureWiFi() {
    const ssid = document.getElementById("ssid").value.trim();
    const password = document.getElementById("wifi-password").value;

    if (!ssid || !password) {
        showAlert("Veuillez remplir tous les champs.", "error");
        return;
    }

    try {
        const response = await fetch("/api/configure-wifi", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ssid: ssid, password: password }),
        });
        const data = await response.json();
        if (response.ok) {
            showAlert(data.message, "success");
        } else {
            showAlert(data.error, "error");
        }
    } catch (err) {
        showAlert("Erreur de connexion au serveur.", "error");
    }
}

async function updateDateTime() {
    const year = document.getElementById("year").value;
    const month = document.getElementById("month").value.padStart(2, "0");
    const day = document.getElementById("day").value.padStart(2, "0");
    const hour = document.getElementById("hour").value.padStart(2, "0");
    const minute = document.getElementById("minute").value.padStart(2, "0");
    const second = document.getElementById("second").value.padStart(2, "0");

    const dt = year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second;

    try {
        const response = await fetch("/api/update-datetime", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ datetime: dt }),
        });
        const data = await response.json();
        if (response.ok) {
            showAlert(data.message, "success");
        } else {
            showAlert(data.error, "error");
        }
    } catch (err) {
        showAlert("Erreur de connexion au serveur.", "error");
    }
}

async function clearData() {
    if (!confirm("Etes-vous sur de vouloir effacer toutes les donnees ? Cette action est irreversible.")) {
        return;
    }

    try {
        const response = await fetch("/api/clear-data", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ confirm: true }),
        });
        const data = await response.json();
        if (response.ok) {
            showAlert(data.message, "success");
        } else {
            showAlert(data.error, "error");
        }
    } catch (err) {
        showAlert("Erreur de connexion au serveur.", "error");
    }
}

async function checkConnection() {
    try {
        const response = await fetch("/api/check-connection");
        const data = await response.json();
        document.getElementById("connection-status").textContent = data.message;
    } catch (err) {
        document.getElementById("connection-status").textContent =
            "Impossible de verifier la connexion.";
    }
}

function initDateTimeForm() {
    const now = new Date();
    document.getElementById("year").value = now.getFullYear();
    document.getElementById("month").value = String(now.getMonth() + 1).padStart(2, "0");
    document.getElementById("day").value = String(now.getDate()).padStart(2, "0");
    document.getElementById("hour").value = String(now.getHours()).padStart(2, "0");
    document.getElementById("minute").value = String(now.getMinutes()).padStart(2, "0");
    document.getElementById("second").value = String(now.getSeconds()).padStart(2, "0");
}

window.addEventListener("load", function () {
    initDateTimeForm();
    checkConnection();
    setInterval(checkConnection, 60000);
});
