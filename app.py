"""
Web Dashboard - Flask application for discovered events (Full Upgrade v5.0)
"""

import os
import json
import threading
import logging
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
import config
from storage import EventStorage
from main import EventDiscoveryPipeline

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'event-scraper-v5-secret'

# Initialize storage
storage = EventStorage()

# Scraping status tracking
SCRAPING_STATUS = {
    'running': False,
    'last_run': None,
    'new_found': 0,
    'current_sector': None,
    'type': 'full' # 'full' or 'free'
}

def get_serper_credits():
    """Read credit usage from log file."""
    log_file = "data/credit_log.json"
    today = datetime.now().strftime("%Y-%m-%d")
    month = datetime.now().strftime("%Y-%m")
    
    usage = {"daily": 0, "monthly": 0}
    if os.path.exists(log_file):
        try:
            with open(log_file) as f:
                log = json.load(f)
                usage["daily"] = log.get("daily", {}).get(today, 0)
                usage["monthly"] = log.get("monthly", {}).get(month, 0)
        except:
            pass
    return usage

# HTML template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E&A Discovery Engine | Premium</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --secondary: #a855f7;
            --dark: #0f172a;
            --light: #f8fafc;
            --success: #22c55e;
            --warning: #f59e0b;
            --danger: #ef4444;
            --info: #3b82f6;
            --platinum: #0ea5e9;
        }

        * {
            margin: 0; padding: 0; box-sizing: border-box;
            font-family: 'Outfit', sans-serif;
        }
        
        body {
            background-color: #f1f5f9;
            color: var(--dark);
            min-height: 100vh;
        }

        .navbar {
            background: rgba(15, 23, 42, 0.9);
            backdrop-filter: blur(10px);
            color: white;
            padding: 15px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }

        .active-tab {
            background: var(--primary) !important;
            color: white !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }

        .brand {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .credit-badge {
            background: rgba(255,255,255,0.1);
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 0.85rem;
            border: 1px solid rgba(255,255,255,0.2);
            display: flex;
            gap: 15px;
        }

        .credit-item span { font-weight: 600; color: #818cf8; }

        .container {
            max-width: 1400px;
            margin: 30px auto;
            padding: 0 20px;
        }

        .top-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: white;
            padding: 25px;
            border-radius: 20px;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
            transition: transform 0.3s;
        }

        .card:hover { transform: translateY(-5px); }

        .card-val { font-size: 2.2rem; font-weight: 700; margin-bottom: 5px; color: var(--dark); }
        .card-label { font-size: 0.9rem; color: #64748b; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }

        .actions-bar {
            background: white;
            padding: 25px;
            border-radius: 20px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }

        .btn-group { display: flex; gap: 12px; }

        .btn {
            padding: 12px 24px;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            border: none;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.95rem;
        }

        .btn-primary { background: var(--primary); color: white; }
        .btn-primary:hover { background: var(--primary-hover); box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4); }
        .btn-secondary { background: #f1f5f9; color: var(--dark); }
        .btn-secondary:hover { background: #e2e8f0; }
        .btn-free { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
        .btn-free:hover { background: #d1fae5; }
        
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }

        .filters-panel {
            background: white;
            padding: 25px;
            border-radius: 20px;
            margin-bottom: 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }

        .filter-item label { display: block; margin-bottom: 8px; font-size: 0.85rem; font-weight: 600; color: #64748b; }
        .filter-item select, .filter-item input {
            width: 100%;
            padding: 12px;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            background: #f8fafc;
            outline: none;
        }

        .table-container {
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        }

        table { width: 100%; border-collapse: collapse; }
        th { background: #f8fafc; padding: 18px 20px; text-align: left; font-size: 0.85rem; font-weight: 700; color: #64748b; text-transform: uppercase; border-bottom: 1px solid #f1f5f9; }
        td { padding: 18px 20px; border-bottom: 1px solid #f1f5f9; font-size: 0.95rem; }
        tr:hover { background: #fdfdfd; }

        .conf-score { display: flex; align-items: center; gap: 8px; font-weight: 600; }
        .dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
        .dot-red { background: var(--danger); }
        .dot-yellow { background: var(--warning); }
        .dot-green { background: var(--success); }
        .dot-blue { background: var(--platinum); }

        .status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
        }
        .status-upcoming { background: #e0f2fe; color: #0369a1; }
        .status-nominations { background: #fef3c7; color: #92400e; }
        .status-concluded { background: #f1f5f9; color: #475569; }

        .type-tag {
            background: #f1f5f9;
            color: #475569;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
            white-space: nowrap;
        }

        .sector-tag {
            background: #eef2ff;
            color: #4338ca;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .countdown {
            font-size: 0.8rem;
            color: var(--danger);
            font-weight: 700;
            margin-top: 4px;
        }

        #statusOverlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(4px);
            z-index: 2000;
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            text-align: center;
        }

        .loader {
            width: 60px; height: 60px;
            border: 5px solid rgba(255,255,255,0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 1s infinite linear;
            margin-bottom: 20px;
        }

        @keyframes spin { to { transform: rotate(360deg); } }

        .toast-container { position: fixed; bottom: 30px; right: 30px; z-index: 3000; }
    </style>
</head>
<body>

    <div id="statusOverlay">
        <div class="loader"></div>
        <h2 id="overlayTitle">Discovery in Progress...</h2>
        <p id="overlayText" style="margin-top: 10px; opacity: 0.8;">Scanning the web for new opportunities</p>
    </div>

    <nav class="navbar">
        <div class="brand">🚀 E&A Discovery Engine</div>
        <div class="credit-badge">
            <div class="credit-item">Today: <span id="creditDaily">0</span> / 80</div>
            <div class="credit-item">Month: <span id="creditMonthly">0</span> / 2400</div>
        </div>
    </nav>

    <div class="container">
        <div class="top-cards">
            <div class="card" style="border-left: 5px solid #f59e0b;">
                <div class="card-val" id="statAwards">0</div>
                <div class="card-label">🏆 Total Awards</div>
            </div>
            <div class="card" style="border-left: 5px solid #6366f1;">
                <div class="card-val" id="statEvents">0</div>
                <div class="card-label">📅 Total Events</div>
            </div>
            <div class="card">
                <div class="card-val" id="statTotal">0</div>
                <div class="card-label">Total Discoveries</div>
            </div>
            <div class="card">
                <div class="card-val" id="statSectors">0</div>
                <div class="card-label">Industries Tracked</div>
            </div>
        </div>

        <div class="actions-bar">
            <div class="btn-group">
                <button class="btn btn-primary" onclick="triggerDiscovery('full')">🔍 Full Discovery Scan</button>
            </div>
            <div class="btn-group">
                <button class="btn btn-secondary" onclick="exportData()">📥 Export CSV</button>
                <button class="btn btn-secondary" style="color: var(--danger); border: 1px solid #fecaca;" onclick="resetEngine()">⚠️ Emergency Reset</button>
            </div>
        </div>

        <div class="filters-panel">
            <div class="filter-item">
                <label>View Category</label>
                <div class="btn-group" style="background: #f1f5f9; padding: 5px; border-radius: 12px;">
                    <button class="btn btn-secondary active-tab" id="tabAll" onclick="setCategory('all')">All</button>
                    <button class="btn btn-secondary" id="tabAwards" onclick="setCategory('Awards')">Awards</button>
                    <button class="btn btn-secondary" id="tabEvents" onclick="setCategory('Event')">Events</button>
                </div>
            </div>
            <div class="filter-item">
                <label>Industry Sector</label>
                <select id="filterSector" onchange="runFilters()">
                    <option value="all">All Sectors</option>
                    {% for sector in sectors %}
                    <option value="{{sector}}">{{sector}}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="filter-item">
                <label>Status</label>
                <select id="filterStatus" onchange="runFilters()">
                    <option value="all">All Status</option>
                    <option value="NOMINATIONS_OPEN">Nominations Open</option>
                    <option value="UPCOMING">Upcoming</option>
                    <option value="CONCLUDED">Concluded</option>
                </select>
            </div>
            <div class="filter-item">
                <label>City / Location</label>
                <select id="filterCity" onchange="runFilters()">
                    <option value="all">All Cities</option>
                    {% for city in cities %}
                    <option value="{{city}}">{{city}}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="filter-item">
                <label>Keyword Search</label>
                <input type="text" id="filterKeyword" placeholder="Search title..." onkeyup="runFilters()">
            </div>
        </div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th style="width: 25%;">Event / Award Name</th>
                        <th>Type</th>
                        <th>Sector</th>
                        <th>Dates</th>
                        <th>Location / Venue</th>
                        <th>Status</th>
                        <th>Confidence</th>
                        <th>Source</th>
                    </tr>
                </thead>
                <tbody id="eventTableBody">
                    <tr><td colspan="8" style="text-align: center; padding: 50px; color: #64748b;">Loading discoveries...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        let allData = [];
        let currentCategory = 'all';

        async function loadData() {
            const [eventsRes, creditsRes] = await Promise.all([
                fetch('/api/events'),
                fetch('/api/credits')
            ]);
            
            allData = await eventsRes.json();
            const credits = await creditsRes.json();

            document.getElementById('creditDaily').textContent = credits.daily;
            document.getElementById('creditMonthly').textContent = credits.monthly;
            
            runFilters();
            updateStats();
        }

        function setCategory(cat) {
            currentCategory = cat;
            document.getElementById('tabAll').classList.remove('active-tab');
            document.getElementById('tabAwards').classList.remove('active-tab');
            document.getElementById('tabEvents').classList.remove('active-tab');
            
            if (cat === 'all') document.getElementById('tabAll').classList.add('active-tab');
            else if (cat === 'Awards') document.getElementById('tabAwards').classList.add('active-tab');
            else document.getElementById('tabEvents').classList.add('active-tab');
            
            runFilters();
        }

        function updateStats() {
            const awardsCount = allData.filter(e => e.event_type === 'Awards').length;
            const eventsCount = allData.filter(e => e.event_type === 'Event').length;
            
            document.getElementById('statTotal').textContent = allData.length;
            document.getElementById('statAwards').textContent = awardsCount;
            document.getElementById('statEvents').textContent = eventsCount;
            document.getElementById('statSectors').textContent = new Set(allData.map(e => e.sector)).size;
        }

        function runFilters() {
            const sector = document.getElementById('filterSector').value;
            const status = document.getElementById('filterStatus').value;
            const keyword = document.getElementById('filterKeyword').value.toLowerCase();

            const filtered = allData.filter(e => {
                const matchCategory = currentCategory === 'all' || e.event_type === currentCategory;
                const matchSector = sector === 'all' || e.sector === sector;
                const matchStatus = status === 'all' || e.status === status;
                const city = document.getElementById('filterCity').value;
                const matchCity = city === 'all' || (e.location && e.location.toLowerCase().includes(city.toLowerCase()));
                const matchKey = !keyword || (e.event_name && e.event_name.toLowerCase().includes(keyword));
                return matchCategory && matchSector && matchStatus && matchCity && matchKey;
            });

            renderTable(filtered);
        }

        function renderTable(data) {
            const tbody = document.getElementById('eventTableBody');
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 50px; color: #64748b;">No matching discoveries found.</td></tr>';
                return;
            }

            tbody.innerHTML = data.map(e => {
                let confClass = 'dot-red';
                if (e.confidence >= 90) confClass = 'dot-blue';
                else if (e.confidence >= 75) confClass = 'dot-green';
                else if (e.confidence >= 50) confClass = 'dot-yellow';

                let statusClass = 'status-upcoming';
                if (e.status === 'NOMINATIONS_OPEN') statusClass = 'status-nominations';
                if (e.status === 'CONCLUDED') statusClass = 'status-concluded';

                const deadline = e.nomination_deadline ? `<div class="countdown">⏰ Deadline: ${e.nomination_deadline}</div>` : '';
                const venue = e.venue ? `<div style="font-size: 0.8rem; color: #64748b; margin-top: 4px;">📍 ${e.venue}</div>` : '';

                return `
                    <tr>
                        <td>
                            <div style="font-weight: 700; color: #1e293b;">${e.event_name}</div>
                            ${deadline}
                        </td>
                        <td><span class="type-tag">${e.event_type || 'Event'}</span></td>
                        <td><span class="sector-tag">${e.sector}</span></td>
                        <td style="font-weight: 500;">${e.date || 'TBD'}</td>
                        <td>
                            <div style="font-weight: 600;">${e.location || 'India'}</div>
                            ${venue}
                        </td>
                        <td><span class="status-badge ${statusClass}">${e.status.replace('_', ' ')}</span></td>
                        <td>
                            <div class="conf-score">
                                <span class="dot ${confClass}"></span>
                                ${e.confidence}%
                            </div>
                        </td>
                        <td><a href="${e.source_url}" target="_blank" style="color: var(--primary); font-weight: 600; text-decoration: none;">Link ↗</a></td>
                    </tr>
                `;
            }).join('');
        }

        async function triggerDiscovery(type) {
            const endpoint = type === 'full' ? '/api/run' : '/api/run_free';
            const res = await fetch(endpoint, { method: 'POST' });
            const status = await res.json();
            
            if (status.status === 'started') {
                document.getElementById('statusOverlay').style.display = 'flex';
                document.getElementById('overlayTitle').textContent = type === 'full' ? 'Deep Search Discovery Active' : 'Quick Free Scan Active';
                pollStatus();
            } else {
                alert(status.message || 'Discovery already running');
            }
        }

        async function pollStatus() {
            const res = await fetch('/api/status');
            const status = await res.json();
            
            if (status.running) {
                document.getElementById('overlayText').innerHTML = `Scanning: <strong>${status.current_sector || 'Initializing...'}</strong><br>New Found: ${status.new_found}`;
                setTimeout(pollStatus, 2000);
            } else {
                document.getElementById('statusOverlay').style.display = 'none';
                loadData();
            }
        }

        function exportData() {
            window.location.href = '/api/export';
        }

        async function resetEngine() {
            if (confirm('Are you sure you want to stop the current discovery engine?')) {
                const res = await fetch('/api/reset', { method: 'POST' });
                const status = await res.json();
                alert(status.message);
                loadData();
            }
        }

        loadData();
        setInterval(loadData, 60000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML, sectors=sorted(config.SECTORS.keys()), cities=sorted(config.CITIES))

@app.route('/api/events')
def get_events():
    return jsonify(storage.get_all_events())

@app.route('/api/credits')
def get_credits():
    return jsonify(get_serper_credits())

@app.route('/api/status')
def get_status():
    status = SCRAPING_STATUS.copy()
    return jsonify(status)

@app.route('/api/run', methods=['POST'])
def run_full():
    if SCRAPING_STATUS['running']:
        return jsonify({'status': 'error', 'message': 'Engine busy'})
    
    SCRAPING_STATUS['type'] = 'full'
    threading.Thread(target=_background_run).start()
    return jsonify({'status': 'started'})

@app.route('/api/reset', methods=['POST'])
def reset_engine():
    """Emergency reset of the busy status."""
    SCRAPING_STATUS['running'] = False
    SCRAPING_STATUS['current_sector'] = None
    return jsonify({'status': 'reset', 'message': 'Engine status cleared'})

@app.route('/api/export')
def export_csv():
    # Force fresh export and return the file
    storage.export_to_csv()
    path = os.path.join(config.DATA_DIR, 'events_export.csv')
    from flask import send_file
    return send_file(path, as_attachment=True, download_name=f"discoveries_{datetime.now().strftime('%Y%H%M')}.csv")

def _background_run():
    SCRAPING_STATUS['running'] = True
    SCRAPING_STATUS['new_found'] = 0
    SCRAPING_STATUS['last_run'] = datetime.now().isoformat()
    
    try:
        pipeline = EventDiscoveryPipeline()
        def on_progress(sector, query):
            SCRAPING_STATUS['current_sector'] = f"{sector}: {query[:25]}"
            
        is_full = (SCRAPING_STATUS['type'] == 'full')
        if is_full:
            # Full scan: Clear local query cache file and force API
            cache_file = "data/query_cache.json"
            if os.path.exists(cache_file):
                try: 
                    os.remove(cache_file)
                except Exception as e:
                    logger.error(f"Failed to clear cache: {e}")
            count = pipeline.run(on_progress=on_progress, force_no_cache=True)
        else:
            # Sector scan: Use force_no_cache=True for manual triggers
            count = pipeline.run(sector=SCRAPING_STATUS['type'], on_progress=on_progress, force_no_cache=True)
            
        SCRAPING_STATUS['new_found'] = count
    except Exception as e:
        logger.error(f"Engine Failure: {e}")
    finally:
        SCRAPING_STATUS['running'] = False
        SCRAPING_STATUS['current_sector'] = None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
