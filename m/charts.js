// Chart.js functionality for metrics dashboard

class MetricsCharts {
    constructor() {
        this.charts = {};
        this.colors = {
            primary: '#007bff',
            secondary: '#6c757d',
            success: '#28a745',
            danger: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
    }

    async loadMetrics(days = 7) {
        try {
            const response = await fetch(`/api/metrics/?days=${days}`);
            if (!response.ok) throw new Error('Failed to load metrics');

            const data = await response.json();
            this.renderCharts(data);
            this.updateSummaryStats(data.summary);

        } catch (error) {
            console.error('Error loading metrics:', error);
            this.showError('Failed to load metrics data');
        }
    }

    renderCharts(data) {
        this.renderMessageChart(data.charts.daily_messages);
        this.renderRatingChart(data.charts.daily_ratings);
        this.renderLanguageChart(data.charts.language_distribution);
        this.renderTopicChart(data.charts.topic_distribution);
    }

    renderMessageChart(chartData) {
        const ctx = document.getElementById('messageChart');
        if (!ctx) return;

        // Destroy existing chart
        if (this.charts.messages) {
            this.charts.messages.destroy();
        }

        this.charts.messages = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Daily Messages',
                    data: chartData.data,
                    borderColor: this.colors.primary,
                    backgroundColor: this.colors.primary + '20',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Daily Message Count'
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    renderRatingChart(chartData) {
        const ctx = document.getElementById('ratingChart');
        if (!ctx) return;

        if (this.charts.ratings) {
            this.charts.ratings.destroy();
        }

        this.charts.ratings = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Average Rating',
                    data: chartData.data,
                    borderColor: this.colors.success,
                    backgroundColor: this.colors.success + '20',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Daily Average Rating'
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        min: 0,
                        max: 5,
                        ticks: {
                            stepSize: 0.5
                        }
                    }
                }
            }
        });
    }

    renderLanguageChart(data) {
        const ctx = document.getElementById('languageChart');
        if (!ctx) return;

        if (this.charts.language) {
            this.charts.language.destroy();
        }

        this.charts.language = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Tamil', 'English'],
                datasets: [{
                    data: [data.tamil, data.english],
                    backgroundColor: [
                        this.colors.primary,
                        this.colors.info
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Language Distribution'
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    renderTopicChart(data) {
        const ctx = document.getElementById('topicChart');
        if (!ctx) return;

        if (this.charts.topics) {
            this.charts.topics.destroy();
        }

        const labels = Object.keys(data);
        const values = Object.values(data);

        // Generate colors for each topic
        const colors = labels.map((_, index) => {
            const colorKeys = Object.keys(this.colors);
            return this.colors[colorKeys[index % colorKeys.length]];
        });

        this.charts.topics = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels.map(label => this.formatTopicLabel(label)),
                datasets: [{
                    label: 'Messages',
                    data: values,
                    backgroundColor: colors.map(color => color + '80'),
                    borderColor: colors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Topic Distribution'
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    },
                    x: {
                        ticks: {
                            maxRotation: 45
                        }
                    }
                }
            }
        });
    }

    updateSummaryStats(summary) {
        // Create or update summary statistics display
        const summaryContainer = document.querySelector('.modal-body');
        if (!summaryContainer) return;

        // Check if summary stats already exist
        let statsDiv = summaryContainer.querySelector('.summary-stats');
        if (!statsDiv) {
            statsDiv = document.createElement('div');
            statsDiv.className = 'summary-stats mb-4';
            summaryContainer.insertBefore(statsDiv, summaryContainer.firstChild);
        }

        statsDiv.innerHTML = `
            <div class="row text-center">
                <div class="col-md-3">
                    <div class="stat-card">
                        <h3 class="text-primary">${summary.total_messages}</h3>
                        <p class="text-muted">Total Messages</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <h3 class="text-success">${summary.average_rating}</h3>
                        <p class="text-muted">Avg Rating</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <h3 class="text-info">${summary.average_response_time}ms</h3>
                        <p class="text-muted">Avg Response Time</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <h3 class="text-warning">${summary.improvement_suggestions.length}</h3>
                        <p class="text-muted">Areas to Improve</p>
                    </div>
                </div>
            </div>
            ${this.renderImprovementSuggestions(summary.improvement_suggestions)}
        `;
    }

    renderImprovementSuggestions(suggestions) {
        if (!suggestions || suggestions.length === 0) {
            return '<div class="alert alert-success mt-3">Great job! No major improvements needed.</div>';
        }

        const suggestionsHtml = suggestions.slice(0, 5).map(suggestion => `
            <div class="improvement-item">
                <div class="d-flex justify-content-between align-items-center">
                    <span class="badge bg-${this.getRatingColor(suggestion.rating)}">${suggestion.rating}/5</span>
                    <small class="text-muted">${suggestion.topic} | ${suggestion.language}</small>
                </div>
                <div class="mt-1">
                    <small><strong>Message:</strong> ${suggestion.message}...</small>
                </div>
                ${suggestion.feedback ? `<div class="mt-1">
                    <small><strong>Feedback:</strong> ${suggestion.feedback}</small>
                </div>` : ''}
            </div>
        `).join('');

        return `
            <div class="mt-4">
                <h6>Areas for Improvement:</h6>
                <div class="improvement-suggestions">
                    ${suggestionsHtml}
                </div>
            </div>
        `;
    }

    getRatingColor(rating) {
        if (rating >= 4) return 'success';
        if (rating >= 3) return 'warning';
        return 'danger';
    }

    formatTopicLabel(topic) {
        return topic.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.textContent = message;

        const modalBody = document.querySelector('.modal-body');
        if (modalBody) {
            modalBody.insertBefore(errorDiv, modalBody.firstChild);
        }
    }

    // Export chart as image
    exportChart(chartName) {
        const chart = this.charts[chartName];
        if (!chart) return;

        const url = chart.toBase64Image();
        const link = document.createElement('a');
        link.href = url;
        link.download = `${chartName}_chart.png`;
        link.click();
    }

    // Update chart data in real-time
    updateChartData(chartName, newData) {
        const chart = this.charts[chartName];
        if (!chart) return;

        chart.data = newData;
        chart.update('active');
    }

    // Resize charts when container changes
    resizeCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.resize();
            }
        });
    }
}

// Global metrics instance
let metricsCharts;

// Initialize metrics when needed
function loadMetrics(days = 7) {
    if (!metricsCharts) {
        metricsCharts = new MetricsCharts();
    }
    metricsCharts.loadMetrics(days);
}

// Handle window resize for charts
window.addEventListener('resize', () => {
    if (metricsCharts) {
        setTimeout(() => {
            metricsCharts.resizeCharts();
        }, 100);
    }
});

// Export all charts
function exportAllCharts() {
    if (!metricsCharts) return;

    Object.keys(metricsCharts.charts).forEach(chartName => {
        setTimeout(() => {
            metricsCharts.exportChart(chartName);
        }, 500);
    });
}

// Add CSS for chart styling
const chartStyles = `
<style>
.stat-card {
    padding: 1rem;
    border-radius: 8px;
    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
    margin-bottom: 1rem;
}

.stat-card h3 {
    font-size: 2rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}

.improvement-suggestions {
    max-height: 300px;
    overflow-y: auto;
}

.improvement-item {
    padding: 0.75rem;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    margin-bottom: 0.5rem;
    background: #f8f9fa;
}

.chart-container {
    position: relative;
    height: 300px;
    margin-bottom: 2rem;
}

@media (max-width: 768px) {
    .chart-container {
        height: 250px;
    }

    .stat-card h3 {
        font-size: 1.5rem;
    }
}
</style>
`;

// Inject chart styles
document.head.insertAdjacentHTML('beforeend', chartStyles);
