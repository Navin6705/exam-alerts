document.addEventListener("DOMContentLoaded", () => {
    // Tab switching
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabPanes = document.querySelectorAll(".tab-pane");

    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.dataset.tab;
            tabBtns.forEach(b => b.classList.remove("active"));
            tabPanes.forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            document.getElementById(target)?.classList.add("active");
        });
    });

    // Provider dropdown toggle
    const providerSelect = document.getElementById("whatsapp_provider");
    const callmebotSection = document.getElementById("callmebot-config");
    const twilioSection = document.getElementById("twilio-config");
    const metaSection = document.getElementById("meta-config");

    function updateProviderSections() {
        const val = providerSelect.value;
        callmebotSection.classList.add("hidden");
        twilioSection.classList.add("hidden");
        metaSection.classList.add("hidden");

        if (val === "callmebot") {
            callmebotSection.classList.remove("hidden");
        } else if (val === "twilio") {
            twilioSection.classList.remove("hidden");
        } else if (val === "meta") {
            metaSection.classList.remove("hidden");
        }
    }

    if (providerSelect) {
        providerSelect.addEventListener("change", updateProviderSections);
        updateProviderSections();
    }

    // Exam Filter Chips
    const chips = document.querySelectorAll("#exam-chips .chip");
    const articles = document.querySelectorAll(".article-card");

    chips.forEach(chip => {
        chip.addEventListener("click", () => {
            chips.forEach(c => c.classList.remove("active"));
            chip.classList.add("active");

            const filter = chip.dataset.filter;
            articles.forEach(card => {
                const cardExam = card.dataset.exam;
                if (filter === "ALL" || cardExam === filter) {
                    card.style.display = "block";
                } else {
                    card.style.display = "none";
                }
            });
        });
    });

    // Scan & Send News Now
    const scanBtn = document.getElementById("scan-now-btn");
    if (scanBtn) {
        scanBtn.addEventListener("click", async () => {
            scanBtn.disabled = true;
            scanBtn.innerHTML = '<span>⏳ Scanning live sources...</span>';

            try {
                const res = await fetch("/api/scan", { method: "POST" });
                const data = await res.json();
                if (data.success) {
                    showToast(`✅ Scan finished: Found ${data.result.new_scraped} new notices, dispatched ${data.result.dispatched} to WhatsApp!`);
                    setTimeout(() => {
                        window.location.reload();
                    }, 1200);
                } else {
                    showToast(`❌ Scan error: ${data.error || "Failed"}`, true);
                }
            } catch (err) {
                showToast(`❌ Request error: ${err.message}`, true);
            } finally {
                scanBtn.disabled = false;
                scanBtn.innerHTML = '<span class="btn-icon">⚡</span><span>Scan & Send News Now</span>';
            }
        });
    }

    // Toggle background auto-monitor
    const toggleWorkerBtn = document.getElementById("toggle-worker-btn");
    const workerDot = document.getElementById("worker-dot");
    const workerStatusText = document.getElementById("worker-status-text");

    if (toggleWorkerBtn) {
        toggleWorkerBtn.addEventListener("click", async () => {
            try {
                const res = await fetch("/api/toggle-bot", { method: "POST" });
                const data = await res.json();
                if (data.success) {
                    const isRunning = data.is_worker_running;
                    workerDot.className = `status-dot ${isRunning ? 'active' : 'inactive'}`;
                    workerStatusText.innerText = isRunning ? "Auto-Monitor: ON" : "Auto-Monitor: OFF";
                    showToast(data.message);
                }
            } catch (err) {
                showToast(`❌ Toggle error: ${err.message}`, true);
            }
        });
    }

    // Test WhatsApp Message
    const testBtn = document.getElementById("test-whatsapp-btn");
    const statusBox = document.getElementById("settings-status-box");

    if (testBtn) {
        testBtn.addEventListener("click", async () => {
            testBtn.disabled = true;
            testBtn.innerHTML = "<span>⏳ Sending test message to WhatsApp...</span>";
            statusBox.className = "status-box info";
            statusBox.innerHTML = "Attempting to send test WhatsApp message...";
            statusBox.classList.remove("hidden");

            try {
                const res = await fetch("/api/test-whatsapp", { method: "POST" });
                const data = await res.json();

                if (data.success) {
                    statusBox.className = "status-box success";
                    statusBox.innerHTML = `✅ <strong>Success!</strong> ${data.message} Check your phone!`;
                    showToast("✅ WhatsApp test message delivered!");
                } else {
                    statusBox.className = "status-box error";
                    statusBox.innerHTML = `❌ <strong>Delivery Failed:</strong> ${data.message}`;
                    showToast("❌ WhatsApp test failed", true);
                }
            } catch (err) {
                statusBox.className = "status-box error";
                statusBox.innerHTML = `❌ <strong>Error:</strong> ${err.message}`;
            } finally {
                testBtn.disabled = false;
                testBtn.innerHTML = "<span>📱 Send Test Message to WhatsApp</span>";
            }
        });
    }

    // Save Settings Form
    const settingsForm = document.getElementById("settings-form");
    if (settingsForm) {
        settingsForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const saveBtn = document.getElementById("save-settings-btn");
            saveBtn.disabled = true;
            saveBtn.innerText = "Saving...";

            const selectedExams = Array.from(document.querySelectorAll("input[name='monitored_exams']:checked")).map(cb => cb.value);

            const payload = {
                whatsapp_provider: document.getElementById("whatsapp_provider").value,
                callmebot_phone: document.getElementById("callmebot_phone")?.value || "",
                callmebot_apikey: document.getElementById("callmebot_apikey")?.value || "",
                twilio_account_sid: document.getElementById("twilio_account_sid")?.value || "",
                twilio_auth_token: document.getElementById("twilio_auth_token")?.value || "",
                twilio_from_number: document.getElementById("twilio_from_number")?.value || "",
                twilio_to_number: document.getElementById("twilio_to_number")?.value || "",
                meta_phone_number_id: document.getElementById("meta_phone_number_id")?.value || "",
                meta_access_token: document.getElementById("meta_access_token")?.value || "",
                meta_recipient_phone: document.getElementById("meta_recipient_phone")?.value || "",
                polling_interval_minutes: parseInt(document.getElementById("polling_interval_minutes").value, 10),
                max_alerts_per_run: parseInt(document.getElementById("max_alerts_per_run").value, 10),
                monitored_exams: selectedExams
            };

            try {
                const res = await fetch("/api/settings", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.success) {
                    statusBox.className = "status-box success";
                    statusBox.innerHTML = "✅ Settings saved successfully!";
                    statusBox.classList.remove("hidden");
                    showToast("Settings saved!");
                } else {
                    statusBox.className = "status-box error";
                    statusBox.innerHTML = `❌ Failed to save: ${data.error}`;
                    statusBox.classList.remove("hidden");
                }
            } catch (err) {
                statusBox.className = "status-box error";
                statusBox.innerHTML = `❌ Request error: ${err.message}`;
                statusBox.classList.remove("hidden");
            } finally {
                saveBtn.disabled = false;
                saveBtn.innerText = "💾 Save Settings";
            }
        });
    }

    // Refresh Feed button
    const refreshBtn = document.getElementById("refresh-feed-btn");
    if (refreshBtn) {
        refreshBtn.addEventListener("click", () => {
            window.location.reload();
        });
    }

    // Toast helper
    function showToast(msg, isError = false) {
        const toast = document.getElementById("toast");
        if (!toast) return;
        toast.innerText = msg;
        toast.style.background = isError ? "#ef4444" : "#0f172a";
        toast.classList.remove("hidden");
        setTimeout(() => {
            toast.classList.add("hidden");
        }, 4000);
    }
});
