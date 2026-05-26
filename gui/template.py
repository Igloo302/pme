# -*- coding: utf-8 -*-
"""HTML template string for Screen Memory GUI - with dark mode, i18n, pipes, stats, timeline."""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Screen Memory GUI</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        :root {
            --bg-gradient-start: #f8fafc;
            --bg-gradient-end: #f1f5f9;
            --body-bg: #f8fafc;
            --card-bg: rgba(255, 255, 255, 0.85);
            --card-border: rgba(15, 23, 42, 0.06);
            --card-shadow: 0 20px 40px rgba(15, 23, 42, 0.05);
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --border-color: rgba(15, 23, 42, 0.08);
            --header-text: #0f172a;
            --search-bg: rgba(241, 245, 249, 0.7);
            
            --accent: #4f46e5;
            --accent-hover: #4338ca;
            --accent-gradient: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
            --accent-light: rgba(79, 70, 229, 0.1);
            
            --danger: #ef4444;
            --danger-hover: #dc2626;
            --danger-gradient: linear-gradient(135deg, #ef4444 0%, #f43f5e 100%);
            
            --success: #10b981;
            --success-pulse: rgba(16, 185, 129, 0.4);
            
            --blob-1-color: rgba(99, 102, 241, 0.1);
            --blob-2-color: rgba(56, 189, 248, 0.1);
            
            --transition-speed: 0.25s;
            --radius-lg: 20px;
            --radius-md: 12px;
            --radius-sm: 8px;
        }

        [data-theme="dark"] {
            --bg-gradient-start: #030712;
            --bg-gradient-end: #0b0f19;
            --body-bg: #030712;
            --card-bg: rgba(17, 24, 39, 0.75);
            --card-border: rgba(255, 255, 255, 0.06);
            --card-shadow: 0 25px 50px rgba(0, 0, 0, 0.35);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --border-color: rgba(255, 255, 255, 0.06);
            --header-text: #f8fafc;
            --search-bg: rgba(31, 41, 55, 0.5);
            
            --accent: #06b6d4;
            --accent-hover: #0891b2;
            --accent-gradient: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
            --accent-light: rgba(6, 182, 212, 0.15);
            
            --danger: #f43f5e;
            --danger-hover: #e11d48;
            --danger-gradient: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%);
            
            --success: #10b981;
            --success-pulse: rgba(16, 185, 129, 0.4);
            
            --blob-1-color: rgba(124, 58, 237, 0.15);
            --blob-2-color: rgba(6, 182, 212, 0.15);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
            background-color: var(--body-bg);
            background-image: radial-gradient(circle at 50% 0%, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
            padding: 40px 20px;
            min-height: 100vh;
            color: var(--text-primary);
            position: relative;
            overflow-x: hidden;
        }

        .bg-blob {
            position: fixed;
            border-radius: 50%;
            filter: blur(140px);
            z-index: -1;
            opacity: 0.55;
            animation: float 20s infinite alternate ease-in-out;
        }
        .bg-blob-1 {
            top: -10%;
            left: -10%;
            width: 40vw;
            height: 40vw;
            background: var(--blob-1-color);
        }
        .bg-blob-2 {
            bottom: -15%;
            right: -10%;
            width: 45vw;
            height: 45vw;
            background: var(--blob-2-color);
            animation-delay: -5s;
            animation-duration: 25s;
        }
        @keyframes float {
            0% { transform: translate(0px, 0px) rotate(0deg) scale(1); }
            50% { transform: translate(30px, -50px) rotate(180deg) scale(1.05); }
            100% { transform: translate(0px, 0px) rotate(360deg) scale(1); }
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: var(--card-bg);
            border-radius: 24px;
            border: 1px solid var(--card-border);
            box-shadow: var(--card-shadow);
            backdrop-filter: blur(20px) saturate(160%);
            -webkit-backdrop-filter: blur(20px) saturate(160%);
            overflow: hidden;
            transition: box-shadow var(--transition-speed);
        }
        
        .header {
            padding: 48px 40px;
            text-align: center;
            position: relative;
            border-bottom: 1px solid var(--border-color);
        }
        .header h1 {
            font-family: 'Outfit', sans-serif;
            font-size: 38px;
            font-weight: 700;
            letter-spacing: -0.03em;
            margin-bottom: 8px;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .header p {
            font-size: 15px;
            color: var(--text-secondary);
            font-weight: 500;
        }
        .header-controls {
            position: absolute;
            top: 24px;
            right: 30px;
            display: flex;
            gap: 12px;
            align-items: center;
        }
        .header-btn {
            background: var(--search-bg);
            border: 1px solid var(--card-border);
            color: var(--text-primary);
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-weight: 600;
            padding: 8px 16px;
            border-radius: 50px;
            cursor: pointer;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all var(--transition-speed) cubic-bezier(0.4, 0, 0.2, 1);
        }
        .header-btn:hover {
            background: var(--text-primary);
            color: var(--body-bg);
            transform: translateY(-1px);
        }
        .quick-control-panel {
            background: var(--card-bg);
            border-radius: var(--radius-lg);
            padding: 20px 30px;
            margin: 30px 40px 0 40px;
            border: 1px solid var(--card-border);
            box-shadow: var(--card-shadow);
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
            transition: all var(--transition-speed) cubic-bezier(0.4, 0, 0.2, 1);
        }
        .quick-control-panel:hover {
            border-color: var(--accent);
        }
        .quick-control-info h3 {
            font-family: 'Outfit', sans-serif;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 4px;
            color: var(--text-primary);
        }
        .quick-control-info p {
            font-size: 12px;
            color: var(--text-secondary);
        }
        .quick-control-actions {
            display: flex;
            gap: 12px;
        }
        .action-btn-glow {
            box-shadow: 0 0 12px rgba(6, 182, 212, 0.35);
        }
        @media (max-width: 768px) {
            .quick-control-panel {
                flex-direction: column;
                align-items: stretch;
                padding: 20px;
                margin: 20px 20px 0 20px;
                text-align: center;
            }
            .quick-control-actions {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            padding: 30px 40px;
        }
        @media (max-width: 768px) {
            .status-grid { grid-template-columns: 1fr; padding: 20px; }
        }
        
        .status-card {
            background: var(--card-bg);
            border-radius: var(--radius-lg);
            padding: 24px;
            border: 1px solid var(--card-border);
            box-shadow: var(--card-shadow);
            transition: all var(--transition-speed) cubic-bezier(0.4, 0, 0.2, 1);
        }
        .status-card:hover {
            transform: translateY(-2px);
            border-color: var(--accent);
        }
        .status-card.active { border-color: var(--success); }
        .status-card h3 {
            font-family: 'Outfit', sans-serif;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
            position: relative;
        }
        .status-indicator.running { background: var(--success); }
        .status-indicator.running::after {
            content: '';
            position: absolute;
            top: -2px; left: -2px; right: -2px; bottom: -2px;
            border-radius: 50%;
            border: 2px solid var(--success);
            animation: pulse 1.8s infinite;
            opacity: 0.8;
        }
        .status-indicator.stopped { background: var(--danger); }
        @keyframes pulse {
            0% { transform: scale(1); opacity: 0.8; }
            100% { transform: scale(2.2); opacity: 0; }
        }
        
        .controls {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 18px;
        }
        
        button {
            padding: 10px 18px;
            border: none;
            border-radius: var(--radius-md);
            font-family: 'Outfit', sans-serif;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all var(--transition-speed) cubic-bezier(0.4, 0, 0.2, 1);
        }
        button:hover { transform: translateY(-1px); }
        button.primary {
            background: var(--accent-gradient);
            color: white;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15);
        }
        [data-theme="dark"] button.primary { box-shadow: 0 4px 12px rgba(6, 182, 212, 0.15); }
        button.primary:hover { box-shadow: 0 6px 16px rgba(79, 70, 229, 0.25); }
        button.danger {
            background: var(--danger-gradient);
            color: white;
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
        }
        button.danger:hover { box-shadow: 0 6px 16px rgba(239, 68, 68, 0.25); }
        button.secondary {
            background: var(--search-bg);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
        }
        button.secondary:hover {
            background: var(--text-primary);
            color: var(--body-bg);
        }
        
        .search-section {
            padding: 30px 40px;
            background: var(--card-bg);
            border-top: 1px solid var(--border-color);
        }
        @media (max-width: 640px) { .search-section { padding: 20px; } }
        
        .main-tabs {
            display: flex;
            gap: 8px;
            padding: 16px 40px;
            background: var(--search-bg);
            border-bottom: 1px solid var(--border-color);
        }
        @media (max-width: 640px) { .main-tabs { padding: 12px 20px; } }
        
        .main-tab {
            padding: 10px 20px;
            background: transparent;
            border: none;
            cursor: pointer;
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 15px;
            color: var(--text-secondary);
            transition: all var(--transition-speed);
            border-radius: 50px;
        }
        .main-tab:hover {
            color: var(--accent);
            background: var(--accent-light);
        }
        .main-tab.active {
            color: white;
            background: var(--accent-gradient);
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
        }
        [data-theme="dark"] .main-tab.active { box-shadow: 0 4px 12px rgba(6, 182, 212, 0.25); }
        
        .tab-content { display: none; }
        .tab-content.active { display: block; animation: fadeIn 0.4s ease-in-out; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .search-tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
        }
        .tab {
            padding: 8px 16px;
            background: var(--search-bg);
            border: 1px solid var(--card-border);
            border-radius: var(--radius-md);
            cursor: pointer;
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            color: var(--text-secondary);
            transition: all var(--transition-speed);
        }
        .tab:hover {
            color: var(--text-primary);
            background: var(--border-color);
        }
        .tab.active {
            background: var(--accent);
            color: white;
            border-color: var(--accent);
        }
        
        .search-box { display: flex; gap: 12px; }
        @media (max-width: 640px) { .search-box { flex-direction: column; } }
        
        input, select {
            padding: 12px 16px;
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 14px;
            background: var(--search-bg);
            color: var(--text-primary);
            transition: all var(--transition-speed);
        }
        input:focus, select:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-light);
            background: var(--card-bg);
        }
        input[type="text"] { flex: 1; }
        
        .results {
            padding: 30px 40px;
            max-height: 600px;
            overflow-y: auto;
        }
        @media (max-width: 640px) { .results { padding: 20px; } }
        
        .result-item {
            background: var(--search-bg);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--accent);
            padding: 20px;
            margin-bottom: 16px;
            border-radius: var(--radius-md);
            transition: all var(--transition-speed);
        }
        .result-item:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
            border-color: var(--accent);
        }
        [data-theme="dark"] .result-item:hover { box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2); }
        .result-meta {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 10px;
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
        }
        .result-meta strong { color: var(--text-primary); }
        .result-content {
            color: var(--text-primary);
            font-size: 14px;
            line-height: 1.6;
            white-space: pre-wrap;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 40px;
            color: var(--text-secondary);
        }
        .empty-state h3 {
            font-family: 'Outfit', sans-serif;
            font-size: 20px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 8px;
        }
        .empty-state p { font-size: 14px; }

        /* Heatmap styles */
        .heatmap-section {
            padding: 30px 40px;
            background: var(--card-bg);
            border-top: 1px solid var(--border-color);
        }
        @media (max-width: 640px) { .heatmap-section { padding: 20px; } }
        .heatmap-section h3 {
            font-family: 'Outfit', sans-serif;
            font-size: 18px;
            margin-bottom: 20px;
        }
        .heatmap-container { overflow-x: auto; padding-bottom: 8px; }
        .heatmap { display: flex; gap: 4px; min-width: max-content; }
        .heatmap-day { display: flex; flex-direction: column; gap: 4px; }
        .heatmap-cell {
            width: 14px; height: 14px; border-radius: 3px;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .heatmap-cell:hover {
            transform: scale(1.3);
            box-shadow: 0 0 8px var(--accent);
            z-index: 10;
        }
        .heatmap-cell.level-0 { background: #e2e8f0; }
        [data-theme="dark"] .heatmap-cell.level-0 { background: #1c1c2b; }
        .heatmap-cell.level-1 { background: #cffafe; }
        [data-theme="dark"] .heatmap-cell.level-1 { background: #0e464c; }
        .heatmap-cell.level-2 { background: #a5f3fc; }
        [data-theme="dark"] .heatmap-cell.level-2 { background: #0f6b75; }
        .heatmap-cell.level-3 { background: #22d3ee; }
        [data-theme="dark"] .heatmap-cell.level-3 { background: #0891b2; }
        .heatmap-cell.level-4 { background: #0891b2; }
        [data-theme="dark"] .heatmap-cell.level-4 { background: #06b6d4; }
        
        .heatmap-cell.today { border: 2px solid var(--accent); }
        .heatmap-labels { display: flex; gap: 4px; margin-top: 8px; }
        .heatmap-labels span {
            width: 14px; font-size: 9px; text-align: center;
            font-weight: 600;
            color: var(--text-secondary);
        }
        .heatmap-legend {
            display: flex; align-items: center; gap: 6px;
            margin-top: 16px; font-size: 12px; color: var(--text-secondary);
            font-weight: 500;
        }
        .heatmap-legend .cell { width: 14px; height: 14px; border-radius: 3px; }
        .heatmap-tooltip {
            position: fixed;
            background: rgba(15, 23, 42, 0.95);
            color: white;
            padding: 10px 14px;
            border-radius: var(--radius-md);
            font-size: 12px;
            font-family: 'Plus Jakarta Sans', sans-serif;
            pointer-events: none;
            z-index: 1000;
            white-space: nowrap;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
        }
        [data-theme="dark"] .heatmap-tooltip {
            background: rgba(255, 255, 255, 0.95);
            color: #0f172a;
            border: 1px solid rgba(0, 0, 0, 0.1);
        }
        .activity-bar {
            display: flex; align-items: center; gap: 12px;
            margin-top: 20px; padding: 16px; background: var(--search-bg);
            border-radius: var(--radius-md);
            border: 1px solid var(--card-border);
        }
        .activity-bar-label {
            font-family: 'Outfit', sans-serif;
            font-size: 13px;
            font-weight: 600;
            color: var(--text-primary);
            width: 60px;
        }
        .activity-bar-track {
            flex: 1; height: 20px; display: flex; gap: 2px;
            border-radius: 6px; overflow: hidden;
        }
        .activity-bar-segment {
            height: 100%; min-width: 3px; transition: all 0.15s;
            border-radius: 1px;
        }
        .activity-bar-segment:hover {
            opacity: 0.8;
            transform: scaleY(1.1);
        }

        /* Pipes section */
        .pipes-section { padding: 30px 40px; }
        @media (max-width: 640px) { .pipes-section { padding: 20px; } }
        
        .pipe-card {
            background: var(--card-bg);
            border-radius: var(--radius-lg);
            padding: 20px;
            margin-bottom: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid var(--border-color);
            box-shadow: var(--card-shadow);
            transition: all var(--transition-speed);
        }
        .pipe-card:hover {
            border-color: var(--accent);
            transform: translateY(-1px);
        }
        .pipe-info h4 {
            font-family: 'Outfit', sans-serif;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 6px;
            color: var(--text-primary);
        }
        .pipe-info p { font-size: 13px; color: var(--text-secondary); }
        .pipe-actions { display: flex; gap: 8px; align-items: center; }

        /* Stats section */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 24px;
            padding: 30px 40px;
        }
        @media (max-width: 640px) { .stats-grid { padding: 20px; } }
        
        .stat-card {
            background: var(--card-bg);
            border-radius: var(--radius-lg);
            padding: 30px 24px;
            text-align: center;
            border: 1px solid var(--border-color);
            box-shadow: var(--card-shadow);
            transition: all var(--transition-speed);
        }
        .stat-card:hover {
            transform: translateY(-2px);
            border-color: var(--accent);
        }
        .stat-value {
            font-family: 'Outfit', sans-serif;
            font-size: 36px;
            font-weight: 700;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }
        .stat-label {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-secondary);
        }

        /* Timeline section */
        .timeline-section { padding: 30px 40px; }
        @media (max-width: 640px) { .timeline-section { padding: 20px; } }
        
        .timeline-date-selector {
            display: flex;
            gap: 12px;
            align-items: center;
            margin-bottom: 30px;
        }
        .timeline-date-selector label {
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 15px;
        }
        .timeline-date-selector input[type="date"] {
            padding: 10px 14px;
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            background: var(--search-bg);
            color: var(--text-primary);
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 14px;
        }
        
        .timeline-group {
            margin-bottom: 30px;
            position: relative;
            padding-left: 20px;
        }
        .timeline-group::before {
            content: '';
            position: absolute;
            top: 15px;
            bottom: 0;
            left: 6px;
            width: 2px;
            background: var(--border-color);
        }
        
        .timeline-date-header {
            font-family: 'Outfit', sans-serif;
            font-size: 16px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 20px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--border-color);
            position: relative;
        }
        
        .timeline-item {
            display: flex;
            gap: 20px;
            padding: 16px 0;
            position: relative;
        }
        .timeline-item::before {
            content: '';
            position: absolute;
            top: 22px;
            left: -18px;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent);
            border: 2px solid var(--body-bg);
            box-shadow: 0 0 0 2px var(--border-color);
            z-index: 2;
        }
        
        .timeline-time {
            font-family: 'Outfit', sans-serif;
            font-size: 13px;
            color: var(--accent);
            font-weight: 600;
            width: 70px;
            flex-shrink: 0;
            padding-top: 2px;
        }
        .timeline-body {
            flex: 1;
            background: var(--search-bg);
            padding: 16px;
            border-radius: var(--radius-md);
            border: 1px solid var(--border-color);
            transition: all var(--transition-speed);
        }
        .timeline-body:hover {
            border-color: var(--accent);
            background: var(--card-bg);
        }
        
        .timeline-app {
            font-family: 'Outfit', sans-serif;
            font-size: 14px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 6px;
        }
        .timeline-text {
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.5;
        }

        .toggle-switch {
            position: relative;
            width: 48px;
            height: 26px;
            background: var(--border-color);
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid var(--card-border);
            padding: 0;
        }
        .toggle-switch.active { background: var(--success); }
        .toggle-switch::after {
            content: '';
            position: absolute;
            top: 2px; left: 2px;
            width: 20px; height: 20px;
            background: white;
            border-radius: 50%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .toggle-switch.active::after { left: 24px; }
    </style>
</head>
<body>
    <div class="bg-blob bg-blob-1"></div>
    <div class="bg-blob bg-blob-2"></div>
    <div class="container">
        <div class="header">
            <div class="header-controls">
                <button class="header-btn" id="lang-toggle" onclick="toggleLang()">EN</button>
                <button class="header-btn" id="theme-toggle" onclick="toggleTheme()">Dark</button>
            </div>
            <h1 id="header-title">Screen Memory GUI</h1>
        </div>

        <div class="main-tabs">
            <button class="main-tab active" onclick="switchMainTab('dashboard')" id="main-tab-dashboard">Dashboard</button>
            <button class="main-tab" onclick="switchMainTab('search')" id="main-tab-search">Search</button>
            <button class="main-tab" onclick="switchMainTab('timeline')" id="main-tab-timeline">Timeline</button>
            <button class="main-tab" onclick="switchMainTab('stats')" id="main-tab-stats">Statistics</button>
            <button class="main-tab" onclick="switchMainTab('pme')" id="main-tab-pme">PME Engine</button>
            <button class="main-tab" onclick="switchMainTab('settings')" id="main-tab-settings">Settings</button>
        </div>

        <!-- Dashboard Tab -->
        <div class="tab-content active" id="tab-dashboard">
            <!-- One-Click Control Panel -->
            <div class="quick-control-panel">
                <div class="quick-control-info">
                    <h3 id="quick-control-title">Unified Control</h3>
                    <p id="quick-control-desc">Launch or stop both recording services simultaneously</p>
                </div>
                <div class="quick-control-actions">
                    <button class="primary action-btn-glow" onclick="startAll()" id="btn-start-all">Start Both</button>
                    <button class="danger" onclick="stopAll()" id="btn-stop-all">Stop Both</button>
                </div>
            </div>

            <div class="status-grid">
                <div class="status-card" id="screenpipe-card">
                    <h3>
                        <span class="status-indicator" id="screenpipe-status"></span>
                        Screenpipe
                    </h3>
                    <div id="screenpipe-info">Checking...</div>
                    <div class="controls">
                        <button class="primary" onclick="startScreenpipe()" id="btn-sp-start">Start</button>
                        <button class="danger" onclick="stopScreenpipe()" id="btn-sp-stop">Stop</button>
                        <button class="danger" onclick="shutdownScreenpipe()" id="btn-sp-shutdown">Shutdown</button>
                        <button class="secondary" onclick="openScreenpipeFolder()" id="btn-sp-folder">Data Folder</button>
                    </div>
                </div>
                <div class="status-card" id="openchronicle-card">
                    <h3>
                        <span class="status-indicator" id="openchronicle-status"></span>
                        OpenChronicle
                    </h3>
                    <div id="openchronicle-info">Checking...</div>
                    <div class="controls">
                        <button class="primary" onclick="startOpenChronicle()" id="btn-oc-start">Start</button>
                        <button class="danger" onclick="stopOpenChronicle()" id="btn-oc-stop">Stop</button>
                        <button class="secondary" onclick="pauseOpenChronicle()" id="btn-oc-pause">Pause</button>
                        <button class="primary" onclick="resumeOpenChronicle()" id="btn-oc-resume">Resume</button>
                        <button class="secondary" onclick="openOpenChronicleFolder()" id="btn-oc-folder">Data Folder</button>
                    </div>
                </div>
            </div>

            <div class="heatmap-section">
                <h3 id="heatmap-title">Activity Heatmap</h3>
                <div class="heatmap-tabs" style="display: flex; gap: 8px; margin-bottom: 16px;">
                    <button class="tab active" onclick="setHeatmapBackend('screenpipe')" id="heatmap-tab-screenpipe">Screenpipe</button>
                    <button class="tab" onclick="setHeatmapBackend('openchronicle')" id="heatmap-tab-openchronicle">OpenChronicle</button>
                </div>
                <div class="heatmap-wrapper" style="display: flex; gap: 12px; margin-top: 16px;">
                    <!-- Hour labels on the left -->
                    <div id="heatmap-hour-labels" style="display: flex; flex-direction: column; font-size: 9px; font-weight: 600; color: var(--text-secondary); text-align: right; width: 28px; shrink: 0; user-select: none;">
                    </div>
                    <!-- Heatmap columns -->
                    <div class="heatmap-container" style="flex: 1; overflow-x: auto; padding-bottom: 8px;">
                        <div class="heatmap" id="heatmap"></div>
                    </div>
                </div>
                <div class="heatmap-legend">
                    <div class="cell level-0"></div>
                    <div class="cell level-1"></div>
                    <div class="cell level-2"></div>
                    <div class="cell level-3"></div>
                    <div class="cell level-4"></div>
                </div>
                <div class="activity-bar" id="activity-bar" style="display:none;">
                    <div class="activity-bar-label" id="activity-bar-label">Today</div>
                    <div class="activity-bar-track" id="activity-bar-track"></div>
                </div>
            </div>

            <!-- PME Auto-Cleaner Status -->
            <div class="status-card" id="auto-cleaner-card" style="margin-top: 24px;">
                <h3>
                    <span class="status-indicator" id="auto-cleaner-status"></span>
                    PME Auto-Cleaner
                    <span style="font-size: 12px; font-weight: 400; color: var(--text-secondary); margin-left: 8px;">Incremental every 5 min</span>
                </h3>
                <div id="auto-cleaner-info" style="margin: 12px 0; color: var(--text-secondary); font-size: 13px;">
                    Initializing...
                </div>
                <div id="auto-cleaner-log" style="max-height: 180px; overflow-y: auto; font-size: 12px; font-family: monospace; background: var(--search-bg); border-radius: var(--radius-sm); padding: 10px; margin-top: 8px;">
                    <span style="color: var(--text-secondary);">Waiting for first run...</span>
                </div>
            </div>
        </div>

        <!-- Search Tab -->
        <div class="tab-content" id="tab-search">
            <div class="search-section" style="border-radius: var(--radius-lg); margin-top: 0; border-top: none;">
                <h3 id="search-title">Search Screen History</h3>
                <div class="search-tabs" style="display: flex; gap: 8px; margin-bottom: 16px;">
                    <button class="tab active" onclick="setSearchBackend('screenpipe')" id="search-tab-screenpipe">Screenpipe</button>
                    <button class="tab" onclick="setSearchBackend('openchronicle')" id="search-tab-openchronicle">OpenChronicle</button>
                    <button class="tab" onclick="setSearchBackend('pme')" id="search-tab-pme">PME Cleaned DB</button>
                </div>
                <div class="search-box">
                    <input type="text" id="query" placeholder="Enter search query..." onkeypress="if(event.key==='Enter')search()">
                    <select id="contentType-screenpipe" style="display:block;">
                        <option value="all">All</option>
                        <option value="ocr">Screen Text</option>
                        <option value="audio">Audio</option>
                    </select>
                    <select id="contentType-openchronicle" style="display:none;">
                        <option value="captures">Screen Captures</option>
                        <option value="entries">Events &amp; Sessions</option>
                        <option value="all">All</option>
                    </select>
                    <select id="contentType-pme" style="display:none;">
                        <option value="all">All</option>
                    </select>
                    <button class="primary" onclick="search()" id="btn-search">Search</button>
                </div>
            </div>

            <div id="results" class="results" style="margin-top: 24px;">
                <div class="empty-state">
                    <h3 id="empty-title">No results yet</h3>
                    <p id="empty-desc">Start recording and search your screen history</p>
                </div>
            </div>
        </div>

        <!-- Timeline Tab -->
        <div class="tab-content" id="tab-timeline">
            <div class="timeline-section">
                <div class="timeline-date-selector">
                    <label id="timeline-label">Date:</label>
                    <input type="date" id="timeline-date">
                    <button class="primary" onclick="loadTimeline()" id="timeline-btn">Load</button>
                </div>
                <div id="timeline-content">
                    <div class="empty-state">
                        <p id="timeline-empty">Select a date and click Load to view timeline</p>
                    </div>
                </div>
            </div>
        </div>



        <!-- Stats Tab -->
        <div class="tab-content" id="tab-stats">
            <div class="stats-grid" id="stats-content">
                <div class="stat-card">
                    <div class="stat-value" id="stat-total">-</div>
                    <div class="stat-label" id="stat-total-label">Total Captures</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="stat-daily">-</div>
                    <div class="stat-label" id="stat-daily-label">Today's Captures</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="stat-weekly">-</div>
                    <div class="stat-label" id="stat-weekly-label">This Week</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="stat-storage">-</div>
                    <div class="stat-label" id="stat-storage-label">Storage (MB)</div>
                </div>
            </div>
        </div>

        <!-- PME Engine Tab -->
        <div class="tab-content" id="tab-pme">
            <div class="stats-grid" style="grid-template-columns: 1fr; max-width: 600px; margin: 0 auto; padding: 30px 40px; gap: 24px;">
                <!-- PME Clean Panel -->
                <div class="stat-card" style="text-align: left; padding: 24px;">
                    <h3 style="font-family: 'Outfit', sans-serif; font-size: 18px; margin-bottom: 16px; font-weight:600; color: var(--accent);">🧹 PME Database Clean</h3>
                    <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 20px; line-height:1.6;">
                        Extract records from Screenpipe & OpenChronicle databases, apply active window multi-frequency OCR strategies and status machine deduplication, then compile an optimized SQLite DB.
                    </p>
                    <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px;">
                        <div style="display: flex; gap: 12px; align-items: center;">
                            <label style="font-size: 13px; font-weight: 600; width: 80px;" id="clean-start-label">Start Time:</label>
                            <input type="datetime-local" id="pme-clean-start" style="padding: 8px 12px; flex: 1;">
                        </div>
                        <div style="display: flex; gap: 12px; align-items: center;">
                            <label style="font-size: 13px; font-weight: 600; width: 80px;" id="clean-end-label">End Time:</label>
                            <input type="datetime-local" id="pme-clean-end" style="padding: 8px 12px; flex: 1;">
                        </div>
                        <button class="primary" onclick="runPMEClean()" id="btn-pme-clean" style="padding: 10px 16px; margin-top: 8px;">Run Cleaning</button>
                    </div>
                    <!-- Cleaning Result Area -->
                    <div id="pme-clean-result" style="display:none; padding: 16px; background: var(--search-bg); border: 1px solid var(--border-color); border-radius: var(--radius-md);">
                        <h4 style="font-family: 'Outfit', sans-serif; font-size: 14px; margin-bottom: 12px; color: var(--accent); font-weight:600;">✓ Cleaning Successful!</h4>
                        <div style="display: grid; grid-template-columns: 1.5fr 1fr; gap: 8px; font-size: 13px;">
                             <div>Raw entries processed:</div><div style="font-weight: 700; text-align: right;" id="clean-stat-raw">-</div>
                             <div>Cleaned DB records:</div><div style="font-weight: 700; text-align: right;" id="clean-stat-cleaned">-</div>
                             <div>Deduplicated (skipped):</div><div style="font-weight: 700; text-align: right;" id="clean-stat-dedup">-</div>
                             <div>Incomplete data discarded:</div><div style="font-weight: 700; text-align: right; color: var(--danger);" id="clean-stat-discarded">-</div>
                             <div>Compression ratio:</div><div style="font-weight: 700; text-align: right; color: var(--success);" id="clean-stat-ratio">-</div>
                        </div>

                        <!-- Save Options -->
                        <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--border-color);">
                            <h4 style="font-family: 'Outfit', sans-serif; font-size: 14px; margin-bottom: 12px; font-weight: 600; color: var(--text-primary);">💾 Save Cleaned Database</h4>
                            <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                                <button class="primary" onclick="downloadCleanedDB()" id="btn-download-db" style="padding: 8px 16px; font-size: 13px;">
                                    ⬇️ Download .db File
                                </button>
                            </div>
                            <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 10px;">Or save directly to a server path:</div>
                            <div style="display: flex; gap: 8px; align-items: center;">
                                <input type="text" id="pme-save-path" placeholder="e.g. ~/Documents/my_memories.db" style="padding: 8px 12px; flex: 1; font-size: 13px; border: 1px solid var(--border-color); border-radius: var(--radius-sm); background: var(--card-bg); color: var(--text-primary);">
                                <button class="secondary" onclick="saveCleanedDBTo()" id="btn-save-db-to" style="padding: 8px 16px; font-size: 13px; white-space: nowrap;">
                                    Save to Path
                                </button>
                            </div>
                            <div id="pme-save-feedback" style="margin-top: 8px; font-size: 12px; display: none;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Settings Tab -->
        <div class="tab-content" id="tab-settings">
            <div class="stats-grid" style="grid-template-columns: 1fr; max-width: 600px; margin: 0 auto; padding: 30px 40px; gap: 24px;">
                <!-- PME Settings Panel -->
                <div class="stat-card" style="text-align: left; padding: 24px;">
                    <h3 style="font-family: 'Outfit', sans-serif; font-size: 18px; margin-bottom: 16px; font-weight:600; color: var(--accent);">⚙️ Configuration Settings</h3>
                    <div style="display: flex; flex-direction: column; gap: 16px; font-size: 13px;">
                        
                        <!-- Group 1: Database Paths -->
                        <div>
                            <div style="font-weight:700; color: var(--accent); margin-bottom: 8px; border-bottom: 1px solid var(--border-color); padding-bottom: 4px;">📂 Database Paths</div>
                            <div style="display: flex; flex-direction: column; gap: 10px;">
                                <div>
                                    <label style="font-weight:600; display:block; margin-bottom:4px;">Screenpipe DB Path</label>
                                    <input type="text" id="cfg-sp-db" style="width: 100%; box-sizing: border-box; padding: 8px 12px;">
                                </div>
                                <div>
                                    <label style="font-weight:600; display:block; margin-bottom:4px;">OpenChronicle DB Path</label>
                                    <input type="text" id="cfg-oc-db" style="width: 100%; box-sizing: border-box; padding: 8px 12px;">
                                </div>
                                <div>
                                    <label style="font-weight:600; display:block; margin-bottom:4px;">PME Output DB Path</label>
                                    <input type="text" id="cfg-pme-db" style="width: 100%; box-sizing: border-box; padding: 8px 12px;">
                                </div>
                            </div>
                        </div>

                        <!-- Group 2: Executables & Services -->
                        <div>
                            <div style="font-weight:700; color: var(--accent); margin-bottom: 8px; border-bottom: 1px solid var(--border-color); padding-bottom: 4px;">🛠️ Binaries & Services</div>
                            <div style="display: flex; flex-direction: column; gap: 10px;">
                                <div>
                                    <label style="font-weight:600; display:block; margin-bottom:4px;">Screenpipe Binary Path</label>
                                    <input type="text" id="cfg-sp-bin" style="width: 100%; box-sizing: border-box; padding: 8px 12px;">
                                </div>
                                <div>
                                    <label style="font-weight:600; display:block; margin-bottom:4px;">OpenChronicle Binary Path</label>
                                    <input type="text" id="cfg-oc-bin" style="width: 100%; box-sizing: border-box; padding: 8px 12px;">
                                </div>
                                <div>
                                    <label style="font-weight:600; display:block; margin-bottom:4px;">Screenpipe API URL</label>
                                    <input type="text" id="cfg-sp-url" style="width: 100%; box-sizing: border-box; padding: 8px 12px;">
                                </div>
                                <div>
                                    <label style="font-weight:600; display:block; margin-bottom:4px;">Screenpipe API Token (Optional)</label>
                                    <input type="password" id="cfg-sp-token" placeholder="Automatically detected if empty" style="width: 100%; box-sizing: border-box; padding: 8px 12px;">
                                </div>
                            </div>
                        </div>

                        <!-- Group 3: Cleaning Policy -->
                        <div>
                            <div style="font-weight:700; color: var(--accent); margin-bottom: 8px; border-bottom: 1px solid var(--border-color); padding-bottom: 4px;">⏱️ Cleaning Policy (seconds)</div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px;">
                                <div>
                                    <label style="font-weight:600; display:block; margin-bottom:4px;">Active Interval</label>
                                    <input type="number" id="cfg-active-int" style="width: 100%; box-sizing: border-box; padding: 8px 12px;">
                                </div>
                                <div>
                                    <label style="font-weight:600; display:block; margin-bottom:4px;">BG Interval</label>
                                    <input type="number" id="cfg-bg-int" style="width: 100%; box-sizing: border-box; padding: 8px 12px;">
                                </div>
                                <div>
                                    <label style="font-weight:600; display:block; margin-bottom:4px;">AX Interval</label>
                                    <input type="number" id="cfg-ax-int" style="width: 100%; box-sizing: border-box; padding: 8px 12px;">
                                </div>
                            </div>
                        </div>

                        <!-- Group 4: AI Engine (LLM) -->
                        <div>
                            <div style="font-weight:700; color: var(--accent); margin-bottom: 8px; border-bottom: 1px solid var(--border-color); padding-bottom: 4px;">🤖 AI Engine (LLM)</div>
                            <div style="display: flex; flex-direction: column; gap: 10px;">
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                                    <div>
                                        <label style="font-weight:600; display:block; margin-bottom:4px;">Provider</label>
                                        <select id="cfg-llm-provider" style="width: 100%; box-sizing: border-box; padding: 8px 12px; border: 1px solid var(--border-color); border-radius: var(--radius-sm); color: var(--text-primary);">
                                            <option value="openai">openai</option>
                                            <option value="deepseek">deepseek</option>
                                            <option value="gemini">gemini</option>
                                            <option value="zhipu">zhipu</option>
                                            <option value="anthropic">anthropic</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label style="font-weight:600; display:block; margin-bottom:4px;">Temperature</label>
                                        <input type="number" id="cfg-llm-temp" step="0.1" min="0" max="1" style="width: 100%; box-sizing: border-box; padding: 8px 12px;">
                                    </div>
                                </div>
                                <div>
                                    <label style="font-weight:600; display:block; margin-bottom:4px;">Model Name</label>
                                    <input type="text" id="cfg-llm-model" style="width: 100%; box-sizing: border-box; padding: 8px 12px;">
                                </div>
                            </div>
                        </div>

                        <div style="display: flex; gap: 12px; margin-top: 12px;">
                            <button class="primary" onclick="savePMEConfig()" id="btn-pme-cfg-save" style="flex:1; padding: 10px;">Save Settings</button>
                            <button class="secondary" onclick="loadPMEConfig()" id="btn-pme-cfg-reset" style="padding: 10px;">Reset</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div id="heatmap-tooltip" class="heatmap-tooltip" style="display:none;"></div>

    <script>
        // ── i18n ────────────────────────────────────────────────────
        var I18N = {
            en: {
                'header.title': 'Screen Memory GUI',
                'header.subtitle': 'Unified control for Screenpipe & OpenChronicle',
                'tab.dashboard': 'Dashboard',
                'tab.search': 'Search',
                'tab.timeline': 'Timeline',
                'tab.pipes': 'Pipes',
                'tab.stats': 'Statistics',
                'quick-control.title': 'Unified Control',
                'quick-control.desc': 'Launch or stop both recording services simultaneously',
                'btn.start_all': 'Start Both',
                'btn.stop_all': 'Stop Both',
                'search.title': 'Search Screen History',
                'search.placeholder': 'Enter search query...',
                'search.btn': 'Search',
                'search.query_required': 'Please enter a search query',
                'empty.title': 'No results yet',
                'empty.desc': 'Start recording and search your screen history',
                'empty.no_results': 'No results found',
                'empty.try_different': 'Try a different search term',
                'heatmap.title': 'Activity Heatmap',
                'activity-bar.label': 'Today',
                'btn.sp_start': 'Start',
                'btn.sp_stop': 'Stop',
                'btn.sp_shutdown': 'Shutdown',
                'btn.sp_folder': 'Data Folder',
                'btn.oc_start': 'Start',
                'btn.oc_stop': 'Stop',
                'btn.oc_pause': 'Pause',
                'btn.oc_resume': 'Resume',
                'btn.oc_folder': 'Data Folder',
                'status.checking': 'Checking...',
                'status.running': 'Running',
                'status.stopped': 'Stopped',
                'sp.shutdown.confirm': 'This will completely shutdown screenpipe. Continue?',
                'pipes.title': 'Screenpipe Pipes',
                'pipes.loading': 'Loading pipes...',
                'pipes.empty': 'No pipes found. Install pipes in ~/.screenpipe/pipes/',
                'pipes.enable': 'Enable',
                'pipes.disable': 'Disable',
                'pipes.schedule': 'Schedule',
                'timeline.title': 'Activity Timeline',
                'timeline.label': 'Date:',
                'timeline.btn': 'Load',
                'timeline.empty': 'Select a date and click Load to view timeline',
                'timeline.no_events': 'No events for this date',
                'stats.total': 'Total Captures',
                'stats.daily': "Today's Captures",
                'stats.weekly': 'This Week',
                'stats.storage': 'Storage (MB)',
                'search.searching': 'Searching...',
                'tab.pme': 'PME Engine',
                'tab.settings': 'Settings',
                'clean.start': 'Start Time:',
                'clean.end': 'End Time:'
            },
            zh: {
                'header.title': '屏幕记忆控制台',
                'header.subtitle': 'Screenpipe 与 OpenChronicle 统一控制面板',
                'tab.dashboard': '控制面板',
                'tab.search': '搜索',
                'tab.timeline': '时间线',
                'tab.pipes': '管道插件',
                'tab.stats': '统计信息',
                'quick-control.title': '一键录制控制',
                'quick-control.desc': '同时启动或停止 Screenpipe 与 OpenChronicle 录制服务',
                'btn.start_all': '一键启动',
                'btn.stop_all': '一键停止',
                'search.title': '搜索屏幕历史',
                'search.placeholder': '输入搜索关键词...',
                'search.btn': '搜索',
                'search.query_required': '请输入搜索关键词',
                'empty.title': '暂无结果',
                'empty.desc': '开始录制后即可搜索屏幕历史',
                'empty.no_results': '未找到结果',
                'empty.try_different': '请尝试其他关键词',
                'heatmap.title': '活动热力图',
                'activity-bar.label': '今天',
                'btn.sp_start': '启动',
                'btn.sp_stop': '停止',
                'btn.sp_shutdown': '关闭',
                'btn.sp_folder': '数据目录',
                'btn.oc_start': '启动',
                'btn.oc_stop': '停止',
                'btn.oc_pause': '暂停',
                'btn.oc_resume': '恢复',
                'btn.oc_folder': '数据目录',
                'status.checking': '检查中...',
                'status.running': '运行中',
                'status.stopped': '已停止',
                'sp.shutdown.confirm': '这将完全关闭 Screenpipe，继续吗？',
                'pipes.title': 'Screenpipe 管道插件',
                'pipes.loading': '加载管道中...',
                'pipes.empty': '未找到管道。请在 ~/.screenpipe/pipes/ 中安装',
                'pipes.enable': '启用',
                'pipes.disable': '禁用',
                'pipes.schedule': '计划',
                'timeline.title': '活动时间线',
                'timeline.label': '日期：',
                'timeline.btn': '加载',
                'timeline.empty': '选择日期后点击查看时间线',
                'timeline.no_events': '当天没有事件',
                'stats.total': '总截屏数',
                'stats.daily': '今日截屏',
                'stats.weekly': '本周截屏',
                'stats.storage': '存储 (MB)',
                'search.searching': '搜索中...',
                'tab.pme': 'PME 引擎',
                'tab.settings': '配置设置',
                'clean.start': '开始时间：',
                'clean.end': '结束时间：'
            }
        };

        var currentLang = localStorage.getItem('smgui-lang') || 'en';
        var currentTheme = localStorage.getItem('smgui-theme') || 'light';

        function t(key) {
            return (I18N[currentLang] && I18N[currentLang][key]) || key;
        }

        function applyI18n() {
            var map = {
                'header-title': 'header.title',
                'main-tab-dashboard': 'tab.dashboard',
                'main-tab-search': 'tab.search',
                'main-tab-timeline': 'tab.timeline',
                'main-tab-pipes': 'tab.pipes',
                'main-tab-stats': 'tab.stats',
                'main-tab-pme': 'tab.pme',
                'main-tab-settings': 'tab.settings',
                'quick-control-title': 'quick-control.title',
                'quick-control-desc': 'quick-control.desc',
                'clean-start-label': 'clean.start',
                'clean-end-label': 'clean.end',
                'search-title': 'search.title',
                'btn-search': 'search.btn',
                'heatmap-title': 'heatmap.title',
                'timeline-label': 'timeline.label',
                'timeline-btn': 'timeline.btn',
                'empty-title': 'empty.title',
                'empty-desc': 'empty.desc',
                'pipes-empty': 'pipes.loading',
                'stat-total-label': 'stats.total',
                'stat-daily-label': 'stats.daily',
                'stat-weekly-label': 'stats.weekly',
                'stat-storage-label': 'stats.storage'
            };
            for (var elId in map) {
                var el = document.getElementById(elId);
                if (el) el.textContent = t(map[elId]);
            }
            var q = document.getElementById('query');
            if (q) q.placeholder = t('search.placeholder');
            // Update buttons
            var btnMap = {
                'btn-sp-start': 'btn.sp_start',
                'btn-sp-stop': 'btn.sp_stop',
                'btn-sp-shutdown': 'btn.sp_shutdown',
                'btn-sp-folder': 'btn.sp_folder',
                'btn-oc-start': 'btn.oc_start',
                'btn-oc-stop': 'btn.oc_stop',
                'btn-oc-pause': 'btn.oc_pause',
                'btn-oc-resume': 'btn.oc_resume',
                'btn-oc-folder': 'btn.oc_folder',
                'btn-start-all': 'btn.start_all',
                'btn-stop-all': 'btn.stop_all'
            };
            for (var bid in btnMap) {
                var bel = document.getElementById(bid);
                if (bel) bel.textContent = t(btnMap[bid]);
            }
        }

        function toggleLang() {
            currentLang = currentLang === 'en' ? 'zh' : 'en';
            localStorage.setItem('smgui-lang', currentLang);
            var btn = document.getElementById('lang-toggle');
            if (btn) btn.textContent = currentLang === 'en' ? 'EN' : '中文';
            applyI18n();
            // Re-render dynamic content if needed
            if (currentMainTab === 'timeline') loadTimeline();
        }

        // ── Theme ───────────────────────────────────────────────────
        function applyTheme() {
            if (currentTheme === 'dark') {
                document.documentElement.setAttribute('data-theme', 'dark');
            } else {
                document.documentElement.removeAttribute('data-theme');
            }
            var btn = document.getElementById('theme-toggle');
            if (btn) btn.textContent = currentTheme === 'dark' ? 'Light' : 'Dark';
        }

        function toggleTheme() {
            currentTheme = currentTheme === 'light' ? 'dark' : 'light';
            localStorage.setItem('smgui-theme', currentTheme);
            applyTheme();
            loadHeatmap();
        }

        // ── Main Tabs ───────────────────────────────────────────────
        var currentMainTab = 'dashboard';

        function switchMainTab(name) {
            currentMainTab = name;
            document.querySelectorAll('.main-tab').forEach(function(t) { t.classList.remove('active'); });
            document.querySelectorAll('.tab-content').forEach(function(c) { c.classList.remove('active'); });
            var tabBtn = document.getElementById('main-tab-' + name);
            if (tabBtn) tabBtn.classList.add('active');
            var tabContent = document.getElementById('tab-' + name);
            if (tabContent) tabContent.classList.add('active');
            if (name === 'stats') loadStats();
            if (name === 'pme') loadPMEConfig();
            if (name === 'settings') loadPMEConfig();
        }

        // ── Search Backend ──────────────────────────────────────────
        let currentBackend = 'screenpipe';

        function setSearchBackend(backend) {
            currentBackend = backend;
            document.querySelectorAll('.search-tabs .tab').forEach(function(t) { t.classList.remove('active'); });
            var tab = document.getElementById('search-tab-' + backend);
            if (tab) tab.classList.add('active');
            document.getElementById('contentType-screenpipe').style.display = backend === 'screenpipe' ? 'block' : 'none';
            document.getElementById('contentType-openchronicle').style.display = backend === 'openchronicle' ? 'block' : 'none';
            document.getElementById('contentType-pme').style.display = backend === 'pme' ? 'block' : 'none';
        }

        // ── Status ──────────────────────────────────────────────────
        function checkStatus() {
            fetch('/api/screenpipe/status')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    var indicator = document.getElementById('screenpipe-status');
                    var info = document.getElementById('screenpipe-info');
                    var card = document.getElementById('screenpipe-card');
                    indicator.className = 'status-indicator ' + (data.running ? 'running' : 'stopped');
                    card.className = 'status-card ' + (data.running ? 'active' : '');
                    info.innerHTML = data.running ? '✓ ' + t('status.running') : '✗ ' + t('status.stopped');
                });

            fetch('/api/openchronicle/status')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    var indicator = document.getElementById('openchronicle-status');
                    var info = document.getElementById('openchronicle-info');
                    var card = document.getElementById('openchronicle-card');
                    indicator.className = 'status-indicator ' + (data.running ? 'running' : 'stopped');
                    card.className = 'status-card ' + (data.running ? 'active' : '');
                    if (data.running) {
                        info.innerHTML = '✓ ' + t('status.running') + ' (PID: ' + (data.pid || 'N/A') + ')<br><small>Captures: ' + (data.buffer_files || 0) + ' files</small>';
                    } else {
                        info.innerHTML = '✗ ' + t('status.stopped');
                    }
                });
        }

        // ── Controls ────────────────────────────────────────────────
        function startScreenpipe() {
            fetch('/api/screenpipe/start', {method: 'POST'}).then(function(r) { return r.json(); }).then(function(d) { alert(d.message); checkStatus(); });
        }
        function stopScreenpipe() {
            fetch('/api/screenpipe/stop', {method: 'POST'}).then(function(r) { return r.json(); }).then(function(d) { alert(d.message); checkStatus(); });
        }
        function shutdownScreenpipe() {
            if (confirm(t('sp.shutdown.confirm'))) {
                fetch('/api/screenpipe/shutdown', {method: 'POST'}).then(function(r) { return r.json(); }).then(function(d) { alert(d.message); checkStatus(); });
            }
        }
        function startOpenChronicle() {
            fetch('/api/openchronicle/start', {method: 'POST'}).then(function(r) { return r.json(); }).then(function(d) { alert(d.message); checkStatus(); });
        }
        function stopOpenChronicle() {
            fetch('/api/openchronicle/stop', {method: 'POST'}).then(function(r) { return r.json(); }).then(function(d) { alert(d.message); checkStatus(); });
        }
        function pauseOpenChronicle() {
            fetch('/api/openchronicle/pause', {method: 'POST'}).then(function(r) { return r.json(); }).then(function(d) { alert(d.message); checkStatus(); });
        }
        function resumeOpenChronicle() {
            fetch('/api/openchronicle/resume', {method: 'POST'}).then(function(r) { return r.json(); }).then(function(d) { alert(d.message); checkStatus(); });
        }
        function openScreenpipeFolder() {
            fetch('/api/screenpipe/open-folder', {method: 'POST'}).then(function(r) { return r.json(); }).then(function(d) { if (d.error) alert(d.error); });
        }
        function openOpenChronicleFolder() {
            fetch('/api/openchronicle/open-folder', {method: 'POST'}).then(function(r) { return r.json(); }).then(function(d) { if (d.error) alert(d.error); });
        }

        // ── Unified Controls ────────────────────────────────────────
        function startAll() {
            var msg = [];
            fetch('/api/screenpipe/start', {method: 'POST'})
                .then(function(r) { return r.json(); })
                .then(function(d) {
                    msg.push('Screenpipe: ' + d.message);
                    return fetch('/api/openchronicle/start', {method: 'POST'});
                })
                .then(function(r) { return r.json(); })
                .then(function(d) {
                    msg.push('OpenChronicle: ' + d.message);
                    alert(msg.join('\\n'));
                    checkStatus();
                })
                .catch(function(err) {
                    alert('Start failed: ' + err);
                    checkStatus();
                });
        }
        function stopAll() {
            var msg = [];
            fetch('/api/screenpipe/stop', {method: 'POST'})
                .then(function(r) { return r.json(); })
                .then(function(d) {
                    msg.push('Screenpipe: ' + d.message);
                    return fetch('/api/openchronicle/stop', {method: 'POST'});
                })
                .then(function(r) { return r.json(); })
                .then(function(d) {
                    msg.push('OpenChronicle: ' + d.message);
                    alert(msg.join('\\n'));
                    checkStatus();
                })
                .catch(function(err) {
                    alert('Stop failed: ' + err);
                    checkStatus();
                });
        }

        // ── Search ──────────────────────────────────────────────────
        function search() {
            var query = document.getElementById('query').value;
            if (!query) { alert(t('search.query_required')); return; }
            var contentTypeSelect = currentBackend === 'screenpipe'
                ? document.getElementById('contentType-screenpipe')
                : (currentBackend === 'openchronicle'
                    ? document.getElementById('contentType-openchronicle')
                    : document.getElementById('contentType-pme'));
            var contentType = contentTypeSelect.value;
            var resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<div class="empty-state"><h3>' + t('search.searching') + '</h3></div>';
            fetch('/api/' + currentBackend + '/search?q=' + encodeURIComponent(query) + '&content_type=' + contentType)
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    var results = data.data || data;
                    if (!results || results.length === 0) {
                        resultsDiv.innerHTML = '<div class="empty-state"><h3>' + t('empty.no_results') + '</h3><p>' + t('empty.try_different') + '</p></div>';
                        return;
                    }
                    resultsDiv.innerHTML = results.map(function(item) {
                        var content = item.content || item;
                        var metaDetails = '';
                        if (item.type === 'Cleaned Memory') {
                            metaDetails = ' | <strong>Trigger:</strong> ' + (content.trigger_reason || 'N/A') + ' | <strong>State:</strong> ' + (content.status || 'Unknown');
                        }
                        return '<div class="result-item">' +
                            '<div class="result-meta">' +
                                '<strong>Time:</strong> ' + (content.timestamp || 'Unknown') + ' | ' +
                                '<strong>App:</strong> ' + (content.app_name || content.app || 'Unknown') + ' | ' +
                                '<strong>Type:</strong> ' + (item.type || 'unknown') +
                                metaDetails +
                            '</div>' +
                            '<div class="result-content">' + escapeHtml((content.text || content.content || '').substring(0, 500)) + '</div>' +
                        '</div>';
                    }).join('');
                })
                .catch(function(err) { alert('Search failed: ' + err); });
        }

        function escapeHtml(text) {
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // ── Heatmap ─────────────────────────────────────────────────
        function getLevel(count, max) {
            if (count === 0 || max === 0) return 0;
            var ratio = count / max;
            if (ratio <= 0.25) return 1;
            if (ratio <= 0.5) return 2;
            if (ratio <= 0.75) return 3;
            return 4;
        }

        function formatHour(h) {
            if (h === 0) return '12a';
            if (h < 12) return h + 'a';
            if (h === 12) return '12p';
            return (h - 12) + 'p';
        }

        function formatDate(d) { return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }); }
        function formatDateZh(d) {
            return (d.getMonth() + 1) + '月' + d.getDate() + '日';
        }

        function getColorForLevel(level) {
            var isDark = currentTheme === 'dark';
            var colors = isDark
                ? ['#1c1c2b', '#0e464c', '#0f6b75', '#0891b2', '#06b6d4']
                : ['#e2e8f0', '#cffafe', '#a5f3fc', '#22d3ee', '#0891b2'];
            return colors[level];
        }

        var tooltipEl = null;

        function showTooltip(e, timeStr, hourData) {
            if (!tooltipEl) tooltipEl = document.getElementById('heatmap-tooltip');
            var appsStr = hourData.apps.length > 0 ? hourData.apps.slice(0, 5).join(', ') : 'No activity';
            tooltipEl.innerHTML = '<strong>' + timeStr + '</strong><br>' + hourData.count + ' captures<br><br>' + appsStr;
            tooltipEl.style.display = 'block';
            moveTooltip(e);
        }
        function moveTooltip(e) {
            if (!tooltipEl) return;
            tooltipEl.style.left = (e.clientX + 12) + 'px';
            tooltipEl.style.top = (e.clientY - 10) + 'px';
        }
        function hideTooltip() { if (tooltipEl) tooltipEl.style.display = 'none'; }

        function renderActivityBar(todayData, maxCount) {
            var barContainer = document.getElementById('activity-bar');
            var barTrack = document.getElementById('activity-bar-track');
            var barLabel = document.getElementById('activity-bar-label');
            if (!todayData) { barContainer.style.display = 'none'; return; }
            barContainer.style.display = 'flex';
            barLabel.textContent = currentLang === 'zh' ? '今天' : t('activity-bar.label');
            barTrack.innerHTML = '';
            todayData.hours.forEach(function(h) {
                if (h.count === 0) return;
                var segment = document.createElement('div');
                segment.className = 'activity-bar-segment';
                var widthPercent = (h.count / maxCount) * 100;
                segment.style.width = Math.max(widthPercent, 2) + '%';
                segment.style.background = getColorForLevel(getLevel(h.count, maxCount));
                segment.title = formatHour(h.hour) + ': ' + h.count + ' captures - ' + h.apps.slice(0, 3).join(', ');
                barTrack.appendChild(segment);
            });
        }

        function renderHeatmap(data) {
            var container = document.getElementById('heatmap');
            var hourLabelsContainer = document.getElementById('heatmap-hour-labels');
            container.innerHTML = '';
            if (hourLabelsContainer) hourLabelsContainer.innerHTML = '';
            if (!data || data.length === 0) {
                container.innerHTML = '<div class="empty-state"><p>No activity data available</p></div>';
                return;
            }
            var maxCount = 0;
            data.forEach(function(day) {
                day.hours.forEach(function(h) { if (h.count > maxCount) maxCount = h.count; });
            });
            data.forEach(function(day, dayIndex) {
                var dayCol = document.createElement('div');
                dayCol.className = 'heatmap-day';
                
                var labelRow = document.createElement('div');
                labelRow.style.height = '12px';
                labelRow.style.marginBottom = '3px';
                labelRow.style.fontSize = '8px';
                labelRow.style.fontWeight = '600';
                labelRow.style.color = 'var(--text-secondary)';
                labelRow.style.textAlign = 'center';
                labelRow.style.whiteSpace = 'nowrap';
                
                if (dayIndex % 5 === 0 || dayIndex === data.length - 1) {
                    var dateObj = new Date(day.date);
                    labelRow.textContent = currentLang === 'zh' ? formatDateZh(dateObj) : formatDate(dateObj);
                }
                dayCol.appendChild(labelRow);

                for (let hour = 0; hour < 24; hour++) {
                    let hourData = day.hours.find(function(h) { return h.hour === hour; }) || { count: 0, apps: [] };
                    let cell = document.createElement('div');
                    let isToday = dayIndex === data.length - 1;
                    cell.className = 'heatmap-cell level-' + getLevel(hourData.count, maxCount) + (isToday ? ' today' : '');
                    let timeStr = day.date + ' ' + formatHour(hour) + '-' + formatHour(hour + 1);
                    cell.addEventListener('mouseenter', function(e) { showTooltip(e, timeStr, hourData); });
                    cell.addEventListener('mouseleave', hideTooltip);
                    cell.addEventListener('mousemove', moveTooltip);
                    dayCol.appendChild(cell);
                }
                container.appendChild(dayCol);
            });

            // Render vertical hour labels on the left
            if (hourLabelsContainer) {
                var headerSpacer = document.createElement('div');
                headerSpacer.style.height = '15px';
                hourLabelsContainer.appendChild(headerSpacer);
                
                for (var hour = 0; hour < 24; hour++) {
                    var hourLabel = document.createElement('div');
                    hourLabel.style.height = '14px';
                    hourLabel.style.lineHeight = '14px';
                    hourLabel.style.marginBottom = '4px'; // Match cell gap (gap: 4px)
                    if (hour % 3 === 0) {
                        hourLabel.textContent = formatHour(hour);
                    }
                    hourLabelsContainer.appendChild(hourLabel);
                }
            }

            renderActivityBar(data[data.length - 1], maxCount);
        }

        let currentHeatmapBackend = 'screenpipe';

        function setHeatmapBackend(backend) {
            currentHeatmapBackend = backend;
            document.querySelectorAll('.heatmap-tabs .tab').forEach(function(t) { t.classList.remove('active'); });
            var tab = document.getElementById('heatmap-tab-' + backend);
            if (tab) tab.classList.add('active');
            loadHeatmap();
        }

        function loadHeatmap() {
            fetch('/api/activity/heatmap?backend=' + currentHeatmapBackend)
                .then(function(r) { return r.json(); })
                .then(function(data) { renderHeatmap(data); })
                .catch(function(err) { console.error('Failed to load heatmap:', err); });
        }

        // ── Auto-Cleaner Status ────────────────────────────────────
        function loadAutoCleanerStatus() {
            fetch('/api/pme/auto-cleaner/status')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    var statusDot = document.getElementById('auto-cleaner-status');
                    var infoDiv = document.getElementById('auto-cleaner-info');
                    var logDiv = document.getElementById('auto-cleaner-log');
                    
                    if (!statusDot || !infoDiv || !logDiv) return;
                    
                    var state = data.state || {};
                    var log = data.log || [];
                    
                    // Update status indicator
                    if (state.running) {
                        statusDot.className = 'status-indicator online';
                    } else if (state.total_runs > 0) {
                        statusDot.className = 'status-indicator';
                        statusDot.style.background = '#f59e0b'; // amber for idle
                    } else {
                        statusDot.className = 'status-indicator';
                    }
                    
                    // Info line
                    var infoText = 'Total runs: ' + (state.total_runs || 0);
                    if (state.last_check) {
                        var lastCheck = state.last_check.split('T')[1];
                        if (lastCheck) infoText += ' | Last check: ' + lastCheck.substring(0, 8);
                    }
                    infoDiv.textContent = infoText;
                    
                    // Render log entries
                    if (log.length === 0) {
                        logDiv.innerHTML = '<span style="color: var(--text-secondary);">Waiting for first run...</span>';
                        return;
                    }
                    
                    var html = '';
                    log.slice().reverse().forEach(function(entry) {
                        var color = '#10b981'; // green
                        var icon = '✅';
                        var detail = '';
                        
                        if (entry.status === 'skipped') {
                            color = '#f59e0b';
                            icon = '⏸️';
                            detail = entry.reason || 'skipped';
                        } else if (entry.status === 'error') {
                            color = '#ef4444';
                            icon = '❌';
                            detail = entry.reason || 'error';
                        } else {
                            detail = 'raw=' + (entry.raw || 0) + ' cleaned=' + (entry.cleaned || 0) + ' discarded=' + (entry.discarded || 0) + ' dedup=' + (entry.dedup || 0);
                        }
                        
                        html += '<div style="color: ' + color + '; padding: 2px 0; border-bottom: 1px solid var(--border-color);">';
                        html += '<span style="opacity: 0.7;">' + entry.time + '</span> ' + icon + ' ' + detail;
                        html += '</div>';
                    });
                    logDiv.innerHTML = html;
                })
                .catch(function(err) { console.error('Failed to load auto-cleaner status:', err); });
        }


        // ── Stats ───────────────────────────────────────────────────
        function loadStats() {
            fetch('/api/stats/summary')
                .then(function(r) { return r.json(); })
                .then(function(stats) {
                    document.getElementById('stat-total').textContent = stats.total_captures || 0;
                    document.getElementById('stat-daily').textContent = stats.daily_captures || 0;
                    document.getElementById('stat-weekly').textContent = stats.weekly_captures || 0;
                    var storageEl = document.getElementById('stat-storage');
                    storageEl.textContent = stats.storage_mb ? stats.storage_mb + ' MB' : 'N/A';
                })
                .catch(function(err) { console.error('Failed to load stats:', err); });
        }

        // ── Timeline ────────────────────────────────────────────────
        function loadTimeline() {
            var date = document.getElementById('timeline-date').value;
            var limit = 50;
            fetch('/api/timeline?date=' + date + '&limit=' + limit)
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    var container = document.getElementById('timeline-content');
                    if (!data.events || data.events.length === 0) {
                        container.innerHTML = '<div class="empty-state"><p>' + t('timeline.no_events') + '</p></div>';
                        return;
                    }
                    var html = '<div class="timeline-group">' +
                        '<div class="timeline-date-header">' + data.date + '</div>';
                    data.events.forEach(function(ev) {
                        var timePart = ev.time ? ev.time.substring(11, 16) : '??:??';
                        html += '<div class="timeline-item">' +
                            '<div class="timeline-time">' + timePart + '</div>' +
                            '<div class="timeline-body">' +
                                '<div class="timeline-app">' + escapeHtml(ev.app_name) + '</div>' +
                                '<div class="timeline-text">' + escapeHtml(ev.text || '') + '</div>' +
                            '</div>' +
                        '</div>';
                    });
                    html += '</div>';
                    container.innerHTML = html;
                })
                .catch(function(err) {
                    document.getElementById('timeline-content').innerHTML =
                        '<div class="empty-state"><p>Error: ' + err + '</p></div>';
                });
        }

        // ── PME Engine Controls ─────────────────────────────────────
        function loadPMEConfig() {
            fetch('/api/config')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    document.getElementById('cfg-sp-db').value = data.database.screenpipe_db || '';
                    document.getElementById('cfg-oc-db').value = data.database.openchronicle_db || '';
                    document.getElementById('cfg-pme-db').value = data.database.cleaned_db || '';
                    document.getElementById('cfg-sp-bin').value = (data.screenpipe && data.screenpipe.bin_path) || '';
                    document.getElementById('cfg-oc-bin').value = (data.openchronicle && data.openchronicle.bin_path) || '';
                    document.getElementById('cfg-sp-url').value = (data.screenpipe && data.screenpipe.api_url) || '';
                    document.getElementById('cfg-sp-token').value = (data.screenpipe && data.screenpipe.api_token) || '';
                    document.getElementById('cfg-active-int').value = (data.cleaning_policy && data.cleaning_policy.active_interval) || 2;
                    document.getElementById('cfg-bg-int').value = (data.cleaning_policy && data.cleaning_policy.bg_interval) || 30;
                    document.getElementById('cfg-ax-int').value = (data.cleaning_policy && data.cleaning_policy.ax_trigger_interval) || 10;
                    document.getElementById('cfg-llm-provider').value = (data.llm && data.llm.provider) || 'openai';
                    document.getElementById('cfg-llm-temp').value = (data.llm && data.llm.temperature !== undefined) ? data.llm.temperature : 0.2;
                    document.getElementById('cfg-llm-model').value = (data.llm && data.llm.model) || '';
                });
        }

        function savePMEConfig() {
            var config = {
                database: {
                    screenpipe_db: document.getElementById('cfg-sp-db').value,
                    openchronicle_db: document.getElementById('cfg-oc-db').value,
                    cleaned_db: document.getElementById('cfg-pme-db').value
                },
                screenpipe: {
                    bin_path: document.getElementById('cfg-sp-bin').value,
                    api_url: document.getElementById('cfg-sp-url').value,
                    api_token: document.getElementById('cfg-sp-token').value
                },
                openchronicle: {
                    bin_path: document.getElementById('cfg-oc-bin').value
                },
                cleaning_policy: {
                    active_interval: parseInt(document.getElementById('cfg-active-int').value) || 2,
                    bg_interval: parseInt(document.getElementById('cfg-bg-int').value) || 30,
                    ax_trigger_interval: parseInt(document.getElementById('cfg-ax-int').value) || 10
                },
                llm: {
                    provider: document.getElementById('cfg-llm-provider').value,
                    temperature: parseFloat(document.getElementById('cfg-llm-temp').value) || 0.2,
                    model: document.getElementById('cfg-llm-model').value
                }
            };
            
            fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                alert(data.message || data.error);
                loadPMEConfig();
            })
            .catch(function(err) { alert('Save settings failed: ' + err); });
        }

        var lastCleanedDBPath = '';

        function runPMEClean() {
            var startTime = document.getElementById('pme-clean-start').value;
            var endTime = document.getElementById('pme-clean-end').value;
            var btn = document.getElementById('btn-pme-clean');
            btn.disabled = true;
            btn.textContent = currentLang === 'zh' ? '处理中...' : 'Processing...';
            
            // Hide previous result and feedback
            document.getElementById('pme-clean-result').style.display = 'none';
            var feedback = document.getElementById('pme-save-feedback');
            if (feedback) { feedback.style.display = 'none'; }
            
            fetch('/api/pme/clean', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ start_time: startTime, end_time: endTime })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                btn.disabled = false;
                btn.textContent = currentLang === 'zh' ? '执行清洗' : 'Run Cleaning';
                if (data.success) {
                    var stats = data.stats;
                    lastCleanedDBPath = data.output_path || '';
                    document.getElementById('pme-clean-result').style.display = 'block';
                    document.getElementById('clean-stat-raw').textContent = stats.raw_records;
                    document.getElementById('clean-stat-cleaned').textContent = stats.cleaned_records;
                    document.getElementById('clean-stat-dedup').textContent = stats.deduplicated;
                    document.getElementById('clean-stat-discarded').textContent = stats.discarded_incomplete_records || 0;
                    var ratio = stats.raw_records / Math.max(1, stats.cleaned_records);
                    document.getElementById('clean-stat-ratio').textContent = ratio.toFixed(2) + 'x';
                    
                    if (typeof loadStats === 'function') loadStats();
                } else {
                    alert(data.message);
                }
            })
            .catch(function(err) {
                btn.disabled = false;
                btn.textContent = currentLang === 'zh' ? '执行清洗' : 'Run Cleaning';
                alert('Error: ' + err);
            });
        }

        function downloadCleanedDB() {
            var url = '/api/pme/clean/download';
            if (lastCleanedDBPath) {
                url += '?path=' + encodeURIComponent(lastCleanedDBPath);
            }
            window.open(url, '_blank');
        }

        function saveCleanedDBTo() {
            var destPath = document.getElementById('pme-save-path').value.trim();
            if (!destPath) {
                alert(currentLang === 'zh' ? '请输入保存路径' : 'Please enter a save path');
                return;
            }
            var feedback = document.getElementById('pme-save-feedback');
            var btn = document.getElementById('btn-save-db-to');
            btn.disabled = true;
            btn.textContent = 'Saving...';
            feedback.style.display = 'none';
            
            fetch('/api/pme/clean/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source: lastCleanedDBPath,
                    destination: destPath
                })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                btn.disabled = false;
                btn.textContent = 'Save to Path';
                feedback.style.display = 'block';
                if (data.success) {
                    feedback.style.color = 'var(--success)';
                    feedback.textContent = '✅ ' + (data.message || 'Saved successfully!');
                } else {
                    feedback.style.color = 'var(--danger)';
                    feedback.textContent = '❌ ' + (data.message || 'Save failed');
                }
            })
            .catch(function(err) {
                btn.disabled = false;
                btn.textContent = 'Save to Path';
                feedback.style.display = 'block';
                feedback.style.color = 'var(--danger)';
                feedback.textContent = '❌ Error: ' + err;
            });
        }

        // ── Initialize ──────────────────────────────────────────────
        function init() {
            applyTheme();
            applyI18n();
            var langBtn = document.getElementById('lang-toggle');
            if (langBtn) langBtn.textContent = currentLang === 'en' ? 'EN' : '中文';
            // Set default timeline date to today
            var dateInput = document.getElementById('timeline-date');
            if (dateInput) dateInput.value = new Date().toISOString().split('T')[0];

            // Set default PME cleaning time: start is 3 days ago, end is now
            var now = new Date();
            var endVal = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
            var threeDaysAgo = new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000);
            var startVal = new Date(threeDaysAgo.getTime() - threeDaysAgo.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
            
            var cleanStart = document.getElementById('pme-clean-start');
            var cleanEnd = document.getElementById('pme-clean-end');
            if (cleanStart) cleanStart.value = startVal;
            if (cleanEnd) cleanEnd.value = endVal;

            checkStatus();
            loadHeatmap();
            loadAutoCleanerStatus();
            setInterval(checkStatus, 10000);
            setInterval(loadHeatmap, 60000);
            setInterval(loadAutoCleanerStatus, 30000);
        }

        init();
    </script>
</body>
</html>"""
