async function searchDomain() {
    const query = document.getElementById("query").value;
    const loading = document.getElementById("loading");
    const resultsDiv = document.getElementById("results");

    if (!query.trim()) {
        resultsDiv.innerHTML = `<div class="message"><i class="fas fa-info-circle"></i> Please enter a domain keyword or name.</div>`;
        return;
    }

    loading.classList.remove("hidden");
    resultsDiv.innerHTML = "";

    const response = await fetch("/search", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ query: query })
    });

    const data = await response.json();
    loading.classList.add("hidden");

    let html = "";

    if (data.message) {
        html += `
            <div class="message">
                <i class="fas fa-bullhorn"></i> ${data.message}
            </div>
        `;
    }

    if (data.results && data.results.length > 0) {
        html += `
            <div class="section-title">
                <i class="fas fa-chart-line"></i> Top Matches
            </div>
            <div class="grid">
        `;
        data.results.forEach(item => {
            html += `
                <div class="card">
                    <div class="domain">${escapeHtml(item.domain)}</div>
                    <div class="status ${item.available ? "available" : "taken"}">
                        ${item.available ? "✓ Available" : "✗ Taken"}
                    </div>
                    <div class="price">
                        <i class="fas fa-tag"></i> Approx Price: ${item.price}
                    </div>
                </div>
            `;
        });
        html += `</div>`;
    }

    if (data.suggestions && data.suggestions.length > 0) {
        html += `
            <div class="section-title">
                <i class="fas fa-lightbulb"></i> Alternative Suggestions
            </div>
            <div class="grid">
        `;
        data.suggestions.forEach(item => {
            html += `
                <div class="card">
                    <div class="domain">${escapeHtml(item.domain)}</div>
                    <div class="status ${item.available ? "available" : "taken"}">
                        ${item.available ? "✓ Available" : "✗ Taken"}
                    </div>
                    <div class="price">
                        <i class="fas fa-tag"></i> Approx Price: ${item.price}
                    </div>
                </div>
            `;
        });
        html += `</div>`;
    }

    if ((!data.results || data.results.length === 0) && (!data.suggestions || data.suggestions.length === 0)) {
        html += `<div class="message"><i class="fas fa-globe"></i> No domains found. Try another keyword.</div>`;
    }

    resultsDiv.innerHTML = html;
    renderGraphAnimation(data.results || [], data.suggestions || []);
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

function renderGraphAnimation(results, suggestions) {
    let existingCanvas = document.getElementById("domainGraphCanvas");
    if (existingCanvas) existingCanvas.remove();

    let graphContainer = document.querySelector(".graph-area");
    if (graphContainer) graphContainer.remove();

    const allDomains = [...results, ...suggestions];
    if (allDomains.length === 0) return;

    const container = document.getElementById("results");
    const graphDiv = document.createElement("div");
    graphDiv.className = "graph-area";
    graphDiv.innerHTML = `
        <div class="graph-title">
            <i class="fas fa-chart-simple"></i> Domain availability radar
        </div>
        <canvas id="domainGraphCanvas" width="500" height="180" style="width:100%; height:180px; border-radius: 16px;"></canvas>
    `;
    container.appendChild(graphDiv);

    const canvas = document.getElementById("domainGraphCanvas");
    const ctx = canvas.getContext("2d");
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = 180;

    const availableCount = allDomains.filter(d => d.available).length;
    const takenCount = allDomains.filter(d => !d.available).length;

    let frame = 0;
    function drawGraph(progress) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const w = canvas.width;
        const h = canvas.height;
        const barWidth = (w - 80) / 2;
        const maxH = h - 40;
        const availH = (availableCount / (availableCount + takenCount || 1)) * maxH * progress;
        const takenH = (takenCount / (availableCount + takenCount || 1)) * maxH * progress;

        ctx.font = "12px 'Inter'";
        ctx.fillStyle = "#334155";
        ctx.fillText("Availability meter", 20, 20);

        ctx.fillStyle = "#dcfce7";
        ctx.fillRect(40, h - availH - 20, barWidth, availH);
        ctx.fillStyle = "#166534";
        ctx.font = "bold 12px 'Inter'";
        ctx.fillText(`Available ${availableCount}`, 40 + 10, h - availH - 28);
        
        ctx.fillStyle = "#fee2e2";
        ctx.fillRect(40 + barWidth + 20, h - takenH - 20, barWidth, takenH);
        ctx.fillStyle = "#991b1b";
        ctx.fillText(`Taken ${takenCount}`, 40 + barWidth + 20 + 10, h - takenH - 28);

        ctx.beginPath();
        ctx.moveTo(30, h - 20);
        ctx.lineTo(w - 20, h - 20);
        ctx.lineTo(w - 20, h - 18);
        ctx.lineTo(30, h - 18);
        ctx.fillStyle = "#94a3b8";
        ctx.fill();

        if (allDomains.length > 0 && progress > 0.2) {
            ctx.beginPath();
            ctx.strokeStyle = "#3b82f6";
            ctx.lineWidth = 2;
            for (let i = 0; i <= 100; i++) {
                let x = 30 + (i / 100) * (w - 60);
                let trend = Math.sin(i * 0.2 + Date.now() * 0.005) * 5 * progress;
                let y = h - 40 - trend - (availableCount / (availableCount + takenCount || 1)) * 30;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();
            ctx.fillStyle = "#2563eb";
            ctx.font = "10px 'Inter'";
            ctx.fillText("domain pulse", w - 80, h - 50);
        }
    }

    let animProgress = 0;
    function animate() {
        animProgress += 0.05;
        if (animProgress >= 1) animProgress = 1;
        drawGraph(animProgress);
        if (animProgress < 1) requestAnimationFrame(animate);
    }
    animate();
}
