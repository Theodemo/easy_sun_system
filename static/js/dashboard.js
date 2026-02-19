"use strict";

async function fetchAndUpdate() {
    try {
        const response = await fetch("/api/update");
        if (!response.ok) throw new Error("HTTP " + response.status);
        const data = await response.json();

        for (const [key, value] of Object.entries(data)) {
            const el = document.getElementById(key);
            if (el) {
                el.textContent = value !== null ? value : "--";
            }
        }
    } catch (err) {
        console.error("Erreur lors de la recuperation des donnees:", err);
    }
}

// Initial fetch + polling every 30 seconds
fetchAndUpdate();
setInterval(fetchAndUpdate, 30000);
