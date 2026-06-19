document.addEventListener("DOMContentLoaded", function () {
    // 1. Highlight Active Route in Sidebar Navigation
    const currentPath = window.location.pathname;
    const navDashboard = document.getElementById("nav-dashboard");
    const navJobs = document.getElementById("nav-jobs");
    const navCandidates = document.getElementById("nav-candidates");
    const navReports = document.getElementById("nav-reports");

    if (currentPath.includes("/dashboard") && navDashboard) navDashboard.classList.add("active");
    else if (currentPath.includes("/jobs") && navJobs) navJobs.classList.add("active");
    else if (currentPath.includes("/candidates") && navCandidates) navCandidates.classList.add("active");
    else if (currentPath.includes("/reports") && navReports) navReports.classList.add("active");

    // 2. Main Dashboard Linear Funnel Chart
    const pipelineCtx = document.getElementById('pipelineChart');
    if (pipelineCtx && window.chartData) {
        new Chart(pipelineCtx, {
            type: 'bar',
            data: {
                labels: window.chartData.labels,
                datasets: [{
                    label: 'Evaluation Breakdown',
                    data: window.chartData.datasets,
                    backgroundColor: ['#10b981', '#34d399', '#f59e0b', '#ef4444'],
                    borderWidth: 0,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true, grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } },
                    x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    // 3. Business Intelligence Analytical Breakdown Pie Graphic
    const reportsPieCtx = document.getElementById('reportsPieChart');
    if (reportsPieCtx && window.pieChartData) {
        new Chart(reportsPieCtx, {
            type: 'doughnut',
            data: {
                labels: window.pieChartData.labels,
                datasets: [{
                    data: window.pieChartData.datasets,
                    backgroundColor: ['#10b981', '#34d399', '#f59e0b', '#ef4444'],
                    borderColor: '#121824',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#94a3b8', font: { family: 'Segoe UI' } } }
                }
            }
        });
    }
});