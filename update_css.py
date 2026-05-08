import sys

with open(r'C:\Users\gian9\OneDrive\Desktop\Proyecto Papi\dashboard_ventas.html', 'r', encoding='utf-8') as f:
    content = f.read()

start_idx = content.find('<link href=\"https://fonts.googleapis.com/css2?family=Syne')
end_idx = content.find('</style>') + len('</style>')

new_css = """<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Roboto+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #f8fafc;
    --surface: #ffffff;
    --surface2: #f1f5f9;
    --border: #e2e8f0;
    --accent: #2563eb;
    --accent2: #059669;
    --accent3: #e11d48;
    --accent4: #8b5cf6;
    --text: #0f172a;
    --muted: #64748b;
    --font-display: 'Inter', sans-serif;
    --font-mono: 'Roboto Mono', monospace;
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--font-display);
    min-height: 100vh;
    overflow-x: hidden;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  body::before {
      display: none;
  }

  .wrapper {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2.5rem 2rem;
  }

  /* Header */
  header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 2.5rem;
    gap: 1rem;
    flex-wrap: wrap;
    border-bottom: 1px solid var(--border);
    padding-bottom: 1.5rem;
  }

  .header-left h1 {
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.025em;
    line-height: 1.2;
    color: var(--text);
  }

  .header-left h1 span {
    color: var(--accent);
  }

  .header-left p {
    margin-top: 0.5rem;
    color: var(--muted);
    font-size: 0.875rem;
    font-weight: 500;
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .upload-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--surface);
    color: var(--text);
    border: 1px solid var(--border);
    font-size: 0.875rem;
    font-weight: 500;
    padding: 0.6rem 1rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: var(--shadow-sm);
  }
  
  .upload-btn:hover {
    background: var(--surface2);
    border-color: #cbd5e1;
  }

  .period-badge {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.5rem 1rem;
    text-align: right;
    box-shadow: var(--shadow-sm);
  }

  .period-badge .label {
    font-size: 0.7rem;
    color: var(--muted);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .period-badge .dates {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text);
    margin-top: 0.1rem;
  }

  /* Empty State */
  .empty-state {
    text-align: center;
    padding: 5rem 2rem;
    background: var(--surface);
    border: 1px dashed #cbd5e1;
    border-radius: 8px;
    margin-bottom: 2rem;
    animation: fadeUp 0.5s ease both;
  }

  .empty-state-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
  }

  .empty-state h2 {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.5rem;
  }

  .empty-state p {
    color: var(--muted);
    font-size: 0.95rem;
    max-width: 500px;
    margin: 0 auto;
    line-height: 1.5;
  }

  /* Dashboard Content */
  .dashboard-content {
    display: none;
  }

  /* KPI Cards */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1.25rem;
    margin-bottom: 2.5rem;
  }

  .kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    position: relative;
    box-shadow: var(--shadow-sm);
    animation: fadeUp 0.5s ease both;
  }

  .kpi-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; bottom: 0;
    width: 4px;
    border-radius: 8px 0 0 8px;
  }

  .kpi-card.c1::after { background: var(--accent); }
  .kpi-card.c2::after { background: var(--accent2); }
  .kpi-card.c3::after { background: var(--accent4); }
  .kpi-card.c4::after { background: var(--accent3); }

  .kpi-label {
    font-size: 0.8rem;
    color: var(--muted);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
  }

  .kpi-value {
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.025em;
    line-height: 1.2;
    color: var(--text);
  }

  .kpi-sub {
    font-size: 0.8rem;
    color: var(--muted);
    margin-top: 0.5rem;
    font-weight: 500;
  }

  /* Table */
  .table-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: var(--shadow-sm);
    animation: fadeUp 0.7s ease both;
    overflow-x: auto;
  }

  .chart-title {
    font-size: 0.8rem;
    color: var(--muted);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.25rem;
  }

  .chart-heading {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--text);
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.875rem;
    margin-top: 1rem;
  }

  thead th {
    text-align: left;
    padding: 0.75rem 1rem;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--muted);
    border-bottom: 2px solid var(--border);
    background: var(--surface2);
  }
  
  thead th:first-child { border-top-left-radius: 6px; }
  thead th:last-child { border-top-right-radius: 6px; }

  thead th.right { text-align: right; }

  tbody tr {
    border-bottom: 1px solid var(--border);
  }

  tbody tr:last-child {
    border-bottom: none;
  }

  tbody td {
    padding: 0.875rem 1rem;
    color: var(--text);
    vertical-align: middle;
  }

  tbody td.right { text-align: right; }
  tbody td.mono { font-family: var(--font-mono); font-weight: 500; font-size: 0.85rem; }

  .rank-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px; height: 24px;
    border-radius: 50%;
    font-family: var(--font-mono);
    font-size: 0.75rem;
    font-weight: 600;
    background: var(--surface2);
    color: var(--muted);
  }

  .rank-num.gold { background: #fef08a; color: #854d0e; }
  .rank-num.silver { background: #e2e8f0; color: #475569; }
  .rank-num.bronze { background: #fed7aa; color: #9a3412; }

  .bar-inline {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .bar-fill {
    height: 6px;
    border-radius: 3px;
    background: var(--accent);
    min-width: 2px;
  }

  /* Rentabilidad section */
  .rentabilidad-section {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: var(--shadow-sm);
    animation: fadeUp 0.8s ease both;
  }

  .section-heading {
    font-size: 0.8rem;
    color: var(--muted);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.25rem;
  }

  .section-title {
    font-size: 1.125rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: var(--text);
  }

  .tips-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.25rem;
  }

  .tip-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1.25rem;
  }

  .tip-icon {
    font-size: 1.25rem;
    margin-bottom: 0.5rem;
  }

  .tip-title {
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
    color: var(--text);
  }

  .tip-body {
    font-size: 0.85rem;
    color: var(--muted);
    line-height: 1.5;
  }

  /* Cost placeholder */
  .cost-placeholder {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 8px;
    padding: 1.5rem;
    text-align: center;
    margin-bottom: 2rem;
    animation: fadeUp 0.9s ease both;
  }

  .cost-placeholder h3 {
    font-size: 1rem;
    font-weight: 600;
    color: #166534;
    margin-bottom: 0.5rem;
  }

  .cost-placeholder p {
    font-size: 0.9rem;
    color: #15803d;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.5;
  }

  /* Footer */
  footer {
    text-align: center;
    padding: 2rem 0 1rem;
    font-size: 0.8rem;
    color: var(--muted);
  }

  /* Animations */
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .kpi-card:nth-child(1) { animation-delay: 0.05s; }
  .kpi-card:nth-child(2) { animation-delay: 0.1s; }
  .kpi-card:nth-child(3) { animation-delay: 0.15s; }
  .kpi-card:nth-child(4) { animation-delay: 0.2s; }
</style>"""

new_content = content[:start_idx] + new_css + content[end_idx:]

with open(r'C:\Users\gian9\OneDrive\Desktop\Proyecto Papi\dashboard_ventas.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated CSS successfully.")
