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
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
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
            transform: translateY(-4px);
            box-shadow: 0 16px 36px rgba(15, 23, 42, 0.08);
            border-color: rgba(79, 70, 229, 0.25);
        }
        [data-theme="dark"] .status-card:hover {
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
            border-color: rgba(6, 182, 212, 0.35);
        }
        .status-card.active { 
            border-color: var(--success);
            box-shadow: 0 12px 28px rgba(16, 185, 129, 0.06), var(--card-shadow);
        }
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
        button:hover { 
            transform: translateY(-1.5px) scale(1.02); 
        }
        button.primary {
            background: var(--accent-gradient);
            color: white;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15);
        }
        [data-theme="dark"] button.primary { box-shadow: 0 4px 12px rgba(6, 182, 212, 0.15); }
        button.primary:hover { 
            box-shadow: 0 8px 20px rgba(79, 70, 229, 0.3); 
        }
        button.danger {
            background: var(--danger-gradient);
            color: white;
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
        }
        button.danger:hover { 
            box-shadow: 0 8px 20px rgba(239, 68, 68, 0.3); 
        }
        button.secondary {
            background: var(--search-bg);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
        }
        button.secondary:hover {
            background: var(--text-primary);
            color: var(--body-bg);
            border-color: var(--text-primary);
        }
        
        .search-section {
            padding: 30px 40px;
            background: var(--card-bg);
            border-top: 1px solid var(--border-color);
        }
        @media (max-width: 640px) { .search-section { padding: 20px; } }
        
        .main-tabs {
            display: flex;
            gap: 6px;
            padding: 6px;
            background: var(--search-bg);
            border: 1px solid var(--border-color);
            border-radius: 50px;
            margin: 24px auto;
            max-width: fit-content;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
        }
        @media (max-width: 640px) { 
            .main-tabs { 
                flex-wrap: wrap; 
                justify-content: center; 
                border-radius: var(--radius-lg); 
                max-width: 92%;
                padding: 10px;
            } 
        }
        
        .main-tab {
            padding: 8px 18px;
            background: transparent;
            border: none;
            cursor: pointer;
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 14px;
            color: var(--text-secondary);
            transition: all var(--transition-speed) cubic-bezier(0.4, 0, 0.2, 1);
            border-radius: 50px;
        }
        .main-tab:hover {
            color: var(--accent);
            background: var(--accent-light);
        }
        .main-tab.active {
            color: white;
            background: var(--accent-gradient);
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
        }
        [data-theme="dark"] .main-tab.active { box-shadow: 0 4px 12px rgba(6, 182, 212, 0.2); }
        
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
            <h1 id="header-title">Personal Memory Engine</h1>
            <p id="header-subtitle">Unified Personal Memory Engine for Screenpipe &amp; OpenChronicle</p>
        </div>

        <div class="main-tabs">
            <button class="main-tab active" onclick="switchMainTab('dashboard')" id="main-tab-dashboard">Dashboard</button>
            <button class="main-tab" onclick="switchMainTab('search')" id="main-tab-search">Search</button>
            <button class="main-tab" onclick="switchMainTab('timeline')" id="main-tab-timeline">Timeline</button>
            <button class="main-tab" onclick="switchMainTab('manual-clean')" id="main-tab-manual-clean">Manual Clean</button>
            <button class="main-tab" onclick="switchMainTab('pipes')" id="main-tab-pipes" style="display: none;">Pipes</button>
            <button class="main-tab" onclick="switchMainTab('stats')" id="main-tab-stats">Statistics</button>
            <button class="main-tab" onclick="switchMainTab('settings')" id="main-tab-settings">Settings</button>
        </div>

        <!-- Dashboard Tab -->
        <div class="tab-content active" id="tab-dashboard">
            <!-- PME Main Switch Card Container -->
            <div style="padding: 30px 40px 0 40px;">
                <div class="status-card" id="pme-main-card" style="margin: 0; padding: 24px; display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; flex-direction: column; gap: 6px;">
                        <h2 style="font-size: 20px; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 10px;">
                            <span class="status-indicator" id="pme-status" style="width: 12px; height: 12px;"></span>
                            <span id="lbl-pme-title">Personal Memory Engine</span>
                        </h2>
                        <div id="pme-info" style="font-size: 14px; color: var(--text-secondary); margin-top: 6px; line-height: 1.5;">Checking...</div>
                    </div>
                    <div>
                        <button class="toggle-switch" id="pme-toggle" onclick="togglePmeAutoClean()"></button>
                    </div>
                </div>
            </div>

            <!-- Services Status Grid -->
            <div class="status-grid" style="margin-bottom: 24px; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
                <div class="status-card" id="screenpipe-card" style="margin: 0;">
                    <h3>
                        <span class="status-indicator" id="screenpipe-status"></span>
                        Screenpipe
                    </h3>
                    <div id="screenpipe-info" style="margin-bottom: 12px;">Checking...</div>
                    <div class="controls">
                        <button class="primary" onclick="startScreenpipe()" id="btn-sp-start">Start</button>
                        <button class="danger" onclick="stopScreenpipe()" id="btn-sp-stop">Stop</button>
                        <button class="secondary" onclick="shutdownScreenpipe()" id="btn-sp-shutdown">Shutdown</button>
                        <button class="secondary" onclick="openScreenpipeFolder()" id="btn-sp-folder">Data Folder</button>
                    </div>
                </div>
                <div class="status-card" id="openchronicle-card" style="margin: 0;">
                    <h3>
                        <span class="status-indicator" id="openchronicle-status"></span>
                        OpenChronicle
                    </h3>
                    <div id="openchronicle-info" style="margin-bottom: 12px;">Checking...</div>
                    <div class="controls">
                        <button class="primary" onclick="startOpenChronicle()" id="btn-oc-start">Start</button>
                        <button class="danger" onclick="stopOpenChronicle()" id="btn-oc-stop">Stop</button>
                        <button class="secondary" onclick="pauseOpenChronicle()" id="btn-oc-pause">Pause</button>
                        <button class="secondary" onclick="resumeOpenChronicle()" id="btn-oc-resume">Resume</button>
                        <button class="secondary" onclick="openOpenChronicleFolder()" id="btn-oc-folder">Data Folder</button>
                    </div>
                </div>
            </div>

            <div class="heatmap-section">
                <div class="heatmap-tabs" style="display: flex; gap: 8px; margin-bottom: 16px;">
                    <button class="tab active" onclick="setHeatmapBackend('pme')" id="heatmap-tab-pme">PME</button>
                    <button class="tab" onclick="setHeatmapBackend('screenpipe')" id="heatmap-tab-screenpipe">Screenpipe</button>
                    <button class="tab" onclick="setHeatmapBackend('openchronicle')" id="heatmap-tab-openchronicle">OpenChronicle</button>
                </div>
                <div class="heatmap-container">
                    <div class="heatmap" id="heatmap"></div>
                </div>
                <div class="heatmap-labels" id="heatmap-labels"></div>
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
        </div>

        <!-- Search Tab -->
        <div class="tab-content" id="tab-search">
            <div class="search-section">
                <h3 id="search-title">Search Screen History</h3>
                <div class="search-tabs">
                    <button class="tab active" onclick="setSearchBackend('pme')" id="tab-pme">PME</button>
                    <button class="tab" onclick="setSearchBackend('screenpipe')" id="tab-screenpipe">Screenpipe</button>
                    <button class="tab" onclick="setSearchBackend('openchronicle')" id="tab-openchronicle">OpenChronicle</button>
                </div>
                <div class="search-box">
                    <input type="text" id="query" placeholder="Enter search query..." onkeypress="if(event.key==='Enter')search()">
                    <select id="contentType-pme" style="display:block;">
                        <option value="all">All</option>
                    </select>
                    <select id="contentType-screenpipe" style="display:none;">
                        <option value="all">All</option>
                        <option value="ocr">Screen Text</option>
                        <option value="audio">Audio</option>
                    </select>
                    <select id="contentType-openchronicle" style="display:none;">
                        <option value="captures">Screen Captures</option>
                        <option value="entries">Events &amp; Sessions</option>
                        <option value="all">All</option>
                    </select>
                    <button class="primary" onclick="search()" id="btn-search">Search</button>
                </div>
            </div>

            <div id="results" class="results">
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

        <!-- Manual Clean Tab -->
        <div class="tab-content" id="tab-manual-clean">
            <div class="pipes-section" style="padding: 24px; max-width: 800px; margin: 0 auto;">
                <h2 style="font-size: 22px; font-weight: 700; margin-bottom: 20px; border-bottom: 1px solid var(--border-color); padding-bottom: 12px;" id="lbl-manual-clean-title">Manual Cleaning</h2>
                
                <div style="display: flex; flex-direction: column; gap: 20px; background: var(--card-bg); padding: 24px; border-radius: var(--radius-md); border: 1px solid var(--border-color); box-shadow: 0 4px 12px rgba(0,0,0,0.01);">
                    <!-- Time Range Selector -->
                    <div style="display: flex; gap: 16px; flex-wrap: wrap;">
                        <div style="flex: 1; min-width: 250px; display: flex; flex-direction: column; gap: 6px;">
                            <label style="font-weight: 600; font-size: 14px;" id="lbl-start-time">Start Time</label>
                            <input type="datetime-local" id="manual-clean-start" style="padding: 10px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary); font-size: 14px;">
                        </div>
                        <div style="flex: 1; min-width: 250px; display: flex; flex-direction: column; gap: 6px;">
                            <label style="font-weight: 600; font-size: 14px;" id="lbl-end-time">End Time</label>
                            <input type="datetime-local" id="manual-clean-end" style="padding: 10px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary); font-size: 14px;">
                        </div>
                    </div>
                    
                    <!-- Phase Selector -->
                    <div style="display: flex; flex-direction: column; gap: 6px;">
                        <label style="font-weight: 600; font-size: 14px;" id="lbl-clean-phase">Cleaning Phase</label>
                        <select id="manual-clean-phase" style="padding: 10px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary); font-size: 14px;">
                            <option value="all">All Due Phases</option>
                            <option value="ingest">Ingest & Filter</option>
                            <option value="cluster">Fact Clustering</option>
                            <option value="observation">Observation Consolidation</option>
                        </select>
                    </div>
                    
                    <!-- Trigger Button -->
                    <div style="margin-top: 10px;">
                        <button class="primary" onclick="triggerManualPmeClean()" id="btn-trigger-manual-clean" style="padding: 12px 24px; font-size: 15px; font-weight: 600; width: 100%;">Clean Now</button>
                    </div>
                </div>
                
                <!-- Manual Clean Progress / Stats -->
                <div id="manual-clean-status-card" style="margin-top: 24px; display: none; background: var(--card-bg); padding: 20px; border-radius: var(--radius-md); border: 1px solid var(--border-color); box-shadow: 0 4px 12px rgba(0,0,0,0.01);">
                    <h3 style="font-size: 16px; font-weight: 700; margin-top: 0; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                        <span class="status-indicator" id="manual-clean-indicator"></span>
                        <span id="lbl-manual-status-title">Cleaning Progress</span>
                    </h3>
                    <div id="manual-clean-info" style="font-size: 14px; color: var(--text-secondary); line-height: 1.6;"></div>
                </div>
            </div>
        </div>

        <!-- Pipes Tab -->
        <div class="tab-content" id="tab-pipes">
            <div class="pipes-section" id="pipes-content">
                <div class="empty-state">
                    <p id="pipes-empty">Loading pipes...</p>
                </div>
            </div>
        </div>

        <!-- Stats Tab -->
        <div class="tab-content" id="tab-stats">
            <div style="padding: 30px 40px; display: flex; flex-direction: column; gap: 40px;">
                <!-- Section: Screenpipe -->
                <div>
                    <h3 style="font-size: 20px; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
                        <span>📺 Screenpipe</span>
                        <small id="stat-sp-status" style="font-size: 12px; font-weight: normal; padding: 2px 8px; border-radius: 12px; background: var(--border-color); color: var(--text-secondary);">Offline</small>
                    </h3>
                    <div class="stats-grid" style="padding: 0; margin-bottom: 20px;">
                        <div class="stat-card">
                            <div class="stat-value" id="stat-sp-total">-</div>
                            <div class="stat-label stat-label-total">Total Captures</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="stat-sp-daily">-</div>
                            <div class="stat-label stat-label-daily">Today's Captures</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="stat-sp-weekly">-</div>
                            <div class="stat-label stat-label-weekly">This Week</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="stat-sp-storage">-</div>
                            <div class="stat-label stat-label-storage">Storage (MB)</div>
                        </div>
                    </div>
                </div>

                <!-- Section: OpenChronicle -->
                <div>
                    <h3 style="font-size: 20px; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
                        <span>⏱️ OpenChronicle</span>
                        <small id="stat-oc-status" style="font-size: 12px; font-weight: normal; padding: 2px 8px; border-radius: 12px; background: var(--border-color); color: var(--text-secondary);">Offline</small>
                    </h3>
                    <div class="stats-grid" style="padding: 0; margin-bottom: 20px;">
                        <div class="stat-card">
                            <div class="stat-value" id="stat-oc-total">-</div>
                            <div class="stat-label stat-label-total">Total Captures</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="stat-oc-daily">-</div>
                            <div class="stat-label stat-label-daily">Today's Captures</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="stat-oc-weekly">-</div>
                            <div class="stat-label stat-label-weekly">This Week</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="stat-oc-storage">-</div>
                            <div class="stat-label stat-label-storage">Storage (MB)</div>
                        </div>
                    </div>
                </div>

                <!-- Section: PME Auto Cleaner -->
                <div>
                    <h3 style="font-size: 20px; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
                        <span>🧠 PME Auto Cleaner (Cleaned)</span>
                        <small id="stat-pme-status" style="font-size: 12px; font-weight: normal; padding: 2px 8px; border-radius: 12px; background: var(--border-color); color: var(--text-secondary);">Active</small>
                    </h3>
                    <div class="stats-grid" style="padding: 0; margin-bottom: 20px;">
                        <div class="stat-card">
                            <div class="stat-value" id="stat-pme-total">-</div>
                            <div class="stat-label stat-label-total">Total Captures</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="stat-pme-daily">-</div>
                            <div class="stat-label stat-label-daily">Today's Captures</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="stat-pme-weekly">-</div>
                            <div class="stat-label stat-label-weekly">This Week</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="stat-pme-storage">-</div>
                            <div class="stat-label stat-label-storage">Storage (MB)</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Settings Tab -->
        <div class="tab-content" id="tab-settings">
            <div style="max-width: 800px; margin: 0 auto; padding: 30px 40px; display: flex; flex-direction: column; gap: 24px;">
                
                <!-- Group 1: Database Paths -->
                <div class="status-card">
                    <h3 style="font-family: 'Outfit', sans-serif; font-size: 18px; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; color: var(--accent);">
                        📂 <span id="lbl-cfg-section-db">Database Paths</span>
                    </h3>
                    <div style="display: flex; flex-direction: column; gap: 16px;">
                        <div>
                            <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);">Screenpipe DB Path</label>
                            <input type="text" id="cfg-sp-db" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);">
                        </div>
                        <div>
                            <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);">OpenChronicle DB Path</label>
                            <input type="text" id="cfg-oc-db" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);">
                        </div>
                        <div>
                            <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);">PME Output DB Path</label>
                            <input type="text" id="cfg-pme-db" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);">
                        </div>
                    </div>
                </div>

                <!-- Group 2: AI Engine Settings -->
                <div class="status-card">
                    <h3 style="font-family: 'Outfit', sans-serif; font-size: 18px; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; color: var(--accent);">
                        🤖 <span id="lbl-cfg-section-llm">AI Engine (LLM) Settings</span>
                    </h3>
                    <div style="display: flex; flex-direction: column; gap: 16px;">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                            <div>
                                <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);">Provider</label>
                                <select id="cfg-llm-provider" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);">
                                    <option value="openai-codex">openai-codex</option>
                                    <option value="openai">openai</option>
                                    <option value="deepseek">deepseek</option>
                                    <option value="gemini">gemini</option>
                                    <option value="anthropic">anthropic</option>
                                    <option value="openrouter">openrouter</option>
                                </select>
                            </div>
                            <div>
                                <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);">Model Name</label>
                                <input type="text" id="cfg-llm-model" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);">
                            </div>
                        </div>
                        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 16px;">
                            <div>
                                <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);">Base URL (Optional)</label>
                                <input type="text" id="cfg-llm-url" placeholder="https://api.openai.com/v1" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);">
                            </div>
                            <div>
                                <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);">Temperature</label>
                                <input type="number" id="cfg-llm-temp" step="0.1" min="0" max="1" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);">
                            </div>
                        </div>
                        <div>
                            <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);">API Key</label>
                            <input type="password" id="cfg-llm-key" placeholder="••••••••••••••••" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);">
                        </div>
                    </div>
                </div>

                <!-- Group 2.5: AI Embedding Settings -->
                <div class="status-card">
                    <h3 style="font-family: 'Outfit', sans-serif; font-size: 18px; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; color: var(--accent);">
                        🧩 <span id="lbl-cfg-section-emb">AI Embedding Settings</span>
                    </h3>
                    <div style="display: flex; flex-direction: column; gap: 16px;">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; align-items: center;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <input type="checkbox" id="cfg-emb-enabled" style="width: 16px; height: 16px; border-radius: 4px; accent-color: var(--accent); cursor: pointer;">
                                <label style="font-size: 13px; font-weight: 500; color: var(--text-primary); cursor: pointer;" for="cfg-emb-enabled" id="lbl-cfg-emb-enabled">Enable Embedding</label>
                            </div>
                            <div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: 12px; align-items: center;">
                                <div style="display: flex; align-items: center; gap: 6px;">
                                    <label style="font-size: 13px; font-weight: 500; color: var(--text-secondary); white-space: nowrap;" id="lbl-cfg-emb-dimensions">Dimensions</label>
                                    <input type="number" id="cfg-emb-dimensions" style="width: 100%; padding: 6px 10px; font-size: 12px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);" placeholder="1536">
                                </div>
                                <div style="display: flex; align-items: center; gap: 6px; justify-content: flex-end;">
                                    <input type="checkbox" id="cfg-emb-normalize" style="width: 14px; height: 14px; accent-color: var(--accent); cursor: pointer;">
                                    <label style="font-size: 13px; font-weight: 500; color: var(--text-secondary); cursor: pointer;" for="cfg-emb-normalize" id="lbl-cfg-emb-normalize">Normalize</label>
                                </div>
                            </div>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                            <div>
                                <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);" id="lbl-cfg-emb-provider">Provider</label>
                                <select id="cfg-emb-provider" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);">
                                    <option value="openai">openai</option>
                                    <option value="openrouter">openrouter</option>
                                    <option value="custom">custom</option>
                                </select>
                            </div>
                            <div>
                                <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);" id="lbl-cfg-emb-model">Model Name</label>
                                <input type="text" id="cfg-emb-model" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);" placeholder="text-embedding-3-small">
                            </div>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: 1.8fr 1.2fr; gap: 16px;">
                            <div>
                                <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);" id="lbl-cfg-emb-url">Base URL (Optional)</label>
                                <input type="text" id="cfg-emb-url" placeholder="https://api.openai.com/v1" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);">
                            </div>
                            <div>
                                <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);" id="lbl-cfg-emb-key-env">API Key Env Var</label>
                                <input type="text" id="cfg-emb-key-env" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);" placeholder="EMBEDDING_API_KEY">
                            </div>
                        </div>
                        
                        <div>
                            <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);" id="lbl-cfg-emb-key">API Key</label>
                            <input type="password" id="cfg-emb-key" placeholder="••••••••••••••••" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);">
                        </div>
                    </div>
                </div>

                <!-- Group 3: PME Auto-Cleaning Schedule -->
                <div class="status-card">
                    <h3 style="font-family: 'Outfit', sans-serif; font-size: 18px; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; color: var(--accent);">
                        ⏱️ <span id="lbl-cfg-section-schedule">PME Auto-Cleaning Schedule</span>
                    </h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px;">
                        <div>
                            <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);" id="lbl-ingest-interval">Ingest (Min):</label>
                            <input type="number" id="pme-ingest-interval" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);" min="1">
                        </div>
                        <div>
                            <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);" id="lbl-cluster-interval">Cluster (Hrs):</label>
                            <input type="number" id="pme-cluster-interval" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);" min="1">
                        </div>
                        <div>
                            <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);" id="lbl-obs-interval">Observation (Hrs):</label>
                            <input type="number" id="pme-obs-interval" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);" min="1">
                        </div>
                    </div>
                </div>

                <!-- Group 4: Executables & Services -->
                <div class="status-card">
                    <h3 style="font-family: 'Outfit', sans-serif; font-size: 18px; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; color: var(--accent);">
                        🛠️ <span id="lbl-cfg-section-services">Executables & Services</span>
                    </h3>
                    <div style="display: flex; flex-direction: column; gap: 16px;">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                            <div>
                                <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);">Screenpipe Binary Path</label>
                                <input type="text" id="cfg-sp-bin" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);">
                            </div>
                            <div>
                                <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);">OpenChronicle Binary Path</label>
                                <input type="text" id="cfg-oc-bin" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);">
                            </div>
                        </div>
                        <div style="display: grid; grid-template-columns: 2fr 1.2fr; gap: 16px;">
                            <div>
                                <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);">Screenpipe API URL</label>
                                <input type="text" id="cfg-sp-url" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);">
                            </div>
                            <div>
                                <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary);">Screenpipe API Token (Optional)</label>
                                <input type="password" id="cfg-sp-token" placeholder="Automatically detected" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--search-bg); color: var(--text-primary);">
                            </div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px; margin-top: 8px;">
                            <input type="checkbox" id="cfg-sp-use-audio" style="width: 16px; height: 16px; border-radius: 4px; accent-color: var(--accent); cursor: pointer;">
                            <label style="font-size: 13px; font-weight: 500; color: var(--text-primary); cursor: pointer;" for="cfg-sp-use-audio" id="lbl-cfg-sp-use-audio">Enable Audio Recording</label>
                        </div>
                    </div>
                </div>

                <div style="text-align: right; margin-top: 10px;">
                    <button class="primary" onclick="savePmeConfig()" id="btn-pme-save-config" style="padding: 12px 30px; font-size: 14px; min-width: 180px; box-shadow: 0 4px 12px var(--accent-light);">Save Settings</button>
                </div>
            </div>
        </div>
    </div>
    <div id="heatmap-tooltip" class="heatmap-tooltip" style="display:none;"></div>

    <script>
        // ── i18n ────────────────────────────────────────────────────
        var I18N = {
            en: {
                'header.title': 'Personal Memory Engine',
                'header.subtitle': 'Unified Personal Memory Engine for Screenpipe & OpenChronicle',
                'tab.dashboard': 'Dashboard',
                'tab.search': 'Search',
                'tab.timeline': 'Timeline',
                'tab.pipes': 'Pipes',
                'tab.stats': 'Statistics',
                'tab.settings': 'Settings',
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
                'pme.title': 'Personal Memory Engine',
                'pme.clean_now': 'Clean Now',
                'pme.settings_title': 'Interval Settings',
                'pme.lbl_ingest': 'Ingest (Min):',
                'pme.lbl_cluster': 'Cluster (Hrs):',
                'pme.lbl_obs': 'Observation (Hrs):',
                'pme.save_settings': 'Save Settings',
                'pme.status.idle': 'Idle',
                'pme.status.running': 'Running...',
                'pme.status.error': 'Error',
                'pme.btn_start': 'Start Auto-Clean',
                'pme.btn_stop': 'Stop Auto-Clean',
                'pme.status.disabled': 'Stopped',
                'tab.manual_clean': 'Manual Clean',
                'lbl.manual_clean_title': 'Manual Cleaning',
                'lbl.start_time': 'Start Time',
                'lbl.end_time': 'End Time',
                'lbl.clean_phase': 'Cleaning Phase',
                'btn.trigger_manual_clean': 'Clean Now',
                'lbl.manual_status_title': 'Cleaning Progress',
                'lbl.pme_title': 'Personal Memory Engine',
                'pme.emb_settings_title': 'AI Embedding Settings',
                'pme.lbl_emb_enabled': 'Enable Embedding',
                'pme.lbl_emb_dimensions': 'Dimensions:',
                'pme.lbl_emb_normalize': 'Normalize',
                'pme.lbl_emb_provider': 'Provider',
                'pme.lbl_emb_model': 'Model Name',
                'pme.lbl_emb_url': 'Base URL (Optional)',
                'pme.lbl_emb_key_env': 'API Key Env Var',
                'pme.lbl_emb_key': 'API Key',
                'pme.lbl_sp_use_audio': 'Enable Audio Recording'
            },
            zh: {
                'header.title': 'Personal Memory Engine',
                'header.subtitle': 'Unified Personal Memory Engine for Screenpipe & OpenChronicle',
                'tab.dashboard': '控制面板',
                'tab.search': '搜索',
                'tab.timeline': '时间线',
                'tab.pipes': '管道插件',
                'tab.stats': '统计信息',
                'tab.settings': '清洗配置',
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
                'pme.title': 'Personal Memory Engine',
                'pme.clean_now': '立即清洗',
                'pme.settings_title': '自动清洗间隔设置',
                'pme.lbl_ingest': '清洗间隔 (分钟):',
                'pme.lbl_cluster': '事实聚类间隔 (小时):',
                'pme.lbl_obs': '生成观察间隔 (小时):',
                'pme.save_settings': '保存设置',
                'pme.status.idle': '空闲',
                'pme.status.running': '清洗中...',
                'pme.status.error': '异常',
                'pme.btn_start': '启动自动清洗',
                'pme.btn_stop': '停止自动清洗',
                'pme.status.disabled': '已停止',
                'tab.manual_clean': '手动清洗',
                'lbl.manual_clean_title': '手动数据清洗',
                'lbl.start_time': '开始时间',
                'lbl.end_time': '结束时间',
                'lbl.clean_phase': '清洗步骤',
                'btn.trigger_manual_clean': '开始清洗',
                'lbl.manual_status_title': '清洗进度',
                'lbl.pme_title': 'Personal Memory Engine',
                'pme.emb_settings_title': 'AI Embedding 配置',
                'pme.lbl_emb_enabled': '启用 Embedding',
                'pme.lbl_emb_dimensions': '维度:',
                'pme.lbl_emb_normalize': '归一化',
                'pme.lbl_emb_provider': '服务商',
                'pme.lbl_emb_model': '模型名称',
                'pme.lbl_emb_url': 'API 基础地址 (可选)',
                'pme.lbl_emb_key_env': 'API Key 环境变量',
                'pme.lbl_emb_key': 'API Key',
                'pme.lbl_sp_use_audio': '启用录音与自动转录'
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
                'header-subtitle': 'header.subtitle',
                'main-tab-dashboard': 'tab.dashboard',
                'main-tab-search': 'tab.search',
                'main-tab-timeline': 'tab.timeline',
                'main-tab-manual-clean': 'tab.manual_clean',
                'main-tab-pipes': 'tab.pipes',
                'main-tab-stats': 'tab.stats',
                'main-tab-settings': 'tab.settings',
                'search-title': 'search.title',
                'btn-search': 'search.btn',
                'timeline-label': 'timeline.label',
                'timeline-btn': 'timeline.btn',
                'empty-title': 'empty.title',
                'empty-desc': 'empty.desc',
                'pipes-empty': 'pipes.loading',
                'pme-settings-title': 'pme.settings_title',
                'lbl-ingest-interval': 'pme.lbl_ingest',
                'lbl-cluster-interval': 'pme.lbl_cluster',
                'lbl-obs-interval': 'pme.lbl_obs',
                'lbl-manual-clean-title': 'lbl.manual_clean_title',
                'lbl-start-time': 'lbl.start_time',
                'lbl-end-time': 'lbl.end_time',
                'lbl-clean-phase': 'lbl.clean_phase',
                'btn-trigger-manual-clean': 'btn.trigger_manual_clean',
                'lbl-manual-status-title': 'lbl.manual_status_title',
                'lbl-pme-title': 'lbl.pme_title',
                'lbl-cfg-section-emb': 'pme.emb_settings_title',
                'lbl-cfg-emb-enabled': 'pme.lbl_emb_enabled',
                'lbl-cfg-emb-dimensions': 'pme.lbl_emb_dimensions',
                'lbl-cfg-emb-normalize': 'pme.lbl_emb_normalize',
                'lbl-cfg-emb-provider': 'pme.lbl_emb_provider',
                'lbl-cfg-emb-model': 'pme.lbl_emb_model',
                'lbl-cfg-emb-url': 'pme.lbl_emb_url',
                'lbl-cfg-emb-key-env': 'pme.lbl_emb_key_env',
                'lbl-cfg-emb-key': 'pme.lbl_emb_key',
                'lbl-cfg-sp-use-audio': 'pme.lbl_sp_use_audio'
            };
            for (var elId in map) {
                var el = document.getElementById(elId);
                if (el) el.textContent = t(map[elId]);
            }
            // Update stats labels using classes
            document.querySelectorAll('.stat-label-total').forEach(function(el) { el.textContent = t('stats.total'); });
            document.querySelectorAll('.stat-label-daily').forEach(function(el) { el.textContent = t('stats.daily'); });
            document.querySelectorAll('.stat-label-weekly').forEach(function(el) { el.textContent = t('stats.weekly'); });
            document.querySelectorAll('.stat-label-storage').forEach(function(el) { el.textContent = t('stats.storage'); });

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
                 'btn-pme-save-config': 'pme.save_settings'
             };
            for (var bid in btnMap) {
                var bel = document.getElementById(bid);
                if (bel) bel.textContent = t(btnMap[bid]);
            }
            // Update select defaults
            var phaseSel = document.getElementById('manual-clean-phase');
            if (phaseSel) {
                phaseSel.options[0].text = currentLang === 'zh' ? '全部未完成流程' : 'All Due Phases';
                phaseSel.options[1].text = currentLang === 'zh' ? '数据采集与过滤 (Ingest)' : 'Ingest & Filter';
                phaseSel.options[2].text = currentLang === 'zh' ? '核心事实聚类 (Clustering)' : 'Fact Clustering';
                phaseSel.options[3].text = currentLang === 'zh' ? '生成每日观察 (Observation)' : 'Observation Consolidation';
            }
            // If currently on stats tab, refresh values to apply translations for status labels
            if (currentMainTab === 'stats') {
                loadStats();
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

        function initManualCleanTimes() {
            var startInput = document.getElementById('manual-clean-start');
            var endInput = document.getElementById('manual-clean-end');
            if (startInput && !startInput.value) {
                var now = new Date();
                var oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
                
                var formatLocal = function(date) {
                    var ten = function(i) { return (i < 10 ? '0' : '') + i; };
                    return date.getFullYear() + '-' +
                        ten(date.getMonth() + 1) + '-' +
                        ten(date.getDate()) + 'T' +
                        ten(date.getHours()) + ':' +
                        ten(date.getMinutes());
                };
                
                startInput.value = formatLocal(oneHourAgo);
                endInput.value = formatLocal(now);
            }

            // Check if PME is currently cleaning (running in background)
            fetch('/api/pme/status')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    if (data.running) {
                        var btn = document.getElementById('btn-trigger-manual-clean');
                        var statusCard = document.getElementById('manual-clean-status-card');
                        var indicator = document.getElementById('manual-clean-indicator');
                        var statusTitle = document.getElementById('lbl-manual-status-title');
                        var info = document.getElementById('manual-clean-info');
                        
                        if (btn) btn.disabled = true;
                        if (statusCard) statusCard.style.display = 'block';
                        if (indicator) indicator.className = 'status-indicator running';
                        if (statusTitle) statusTitle.textContent = currentLang === 'zh' ? '正在清洗...' : 'Cleaning...';
                        
                        var phaseText = data.last_run_phase || 'all';
                        if (info) info.innerHTML = (currentLang === 'zh' ? '后台清洗任务正在运行。步骤: ' : 'Background cleaner is running. Phase: ') + phaseText;
                        
                        if (manualCleanInterval) clearInterval(manualCleanInterval);
                        manualCleanInterval = setInterval(pollManualCleanStatus, 1000);
                    }
                });
        }

        function switchMainTab(name) {
            currentMainTab = name;
            document.querySelectorAll('.main-tab').forEach(function(t) { t.classList.remove('active'); });
            document.querySelectorAll('.tab-content').forEach(function(c) { c.classList.remove('active'); });
            var tabBtn = document.getElementById('main-tab-' + name);
            if (tabBtn) tabBtn.classList.add('active');
            var tabContent = document.getElementById('tab-' + name);
            if (tabContent) tabContent.classList.add('active');
            if (name === 'pipes') loadPipes();
            if (name === 'stats') loadStats();
            if (name === 'manual-clean') initManualCleanTimes();
        }

        // ── Search Backend ──────────────────────────────────────────
        let currentBackend = 'pme';

        function setSearchBackend(backend) {
            currentBackend = backend;
            document.querySelectorAll('.search-tabs .tab').forEach(function(t) { t.classList.remove('active'); });
            var tab = document.getElementById('tab-' + backend);
            if (tab) tab.classList.add('active');
            document.getElementById('contentType-pme').style.display = backend === 'pme' ? 'block' : 'none';
            document.getElementById('contentType-screenpipe').style.display = backend === 'screenpipe' ? 'block' : 'none';
            document.getElementById('contentType-openchronicle').style.display = backend === 'openchronicle' ? 'block' : 'none';
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

        // ── Search ──────────────────────────────────────────────────
        function search() {
            var query = document.getElementById('query').value;
            if (!query) { alert(t('search.query_required')); return; }
            var contentTypeSelect = document.getElementById('contentType-' + currentBackend);
            var contentType = contentTypeSelect ? contentTypeSelect.value : 'all';
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
                        return '<div class="result-item">' +
                            '<div class="result-meta">' +
                                '<strong>Time:</strong> ' + (content.timestamp || 'Unknown') + ' | ' +
                                '<strong>App:</strong> ' + (content.app_name || content.app || 'Unknown') + ' | ' +
                                '<strong>Type:</strong> ' + (item.type || 'unknown') +
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
            var labelsContainer = document.getElementById('heatmap-labels');
            container.innerHTML = '';
            labelsContainer.innerHTML = '';
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
                if (dayIndex === 0) {
                    var labelRow = document.createElement('div');
                    labelRow.style.height = '12px';
                    labelRow.style.marginBottom = '3px';
                    dayCol.appendChild(labelRow);
                }
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
            for (var hour = 0; hour < 24; hour++) {
                var label = document.createElement('span');
                if (hour % 3 === 0) label.textContent = formatHour(hour);
                labelsContainer.appendChild(label);
            }
            renderActivityBar(data[data.length - 1], maxCount);
        }

        let currentHeatmapBackend = 'pme';

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

        // ── Pipes ───────────────────────────────────────────────────
        function loadPipes() {
            fetch('/api/screenpipe/pipes')
                .then(function(r) { return r.json(); })
                .then(function(pipes) {
                    var container = document.getElementById('pipes-content');
                    if (!pipes || pipes.length === 0) {
                        container.innerHTML = '<div class="empty-state"><p>' + t('pipes.empty') + '</p></div>';
                        return;
                    }
                    var html = '';
                    pipes.forEach(function(pipe) {
                        var safeName = pipe.name.replace(/'/g, "\\'");
                        var actionBtn = pipe.enabled ? t('pipes.disable') : t('pipes.enable');
                        html += '<div class="pipe-card">' +
                            '<div class="pipe-info">' +
                                '<h4>' + escapeHtml(pipe.name) + '</h4>' +
                                '<p>' + escapeHtml(pipe.description || pipe.name);
                        if (pipe.schedule) {
                            html += ' | ' + t('pipes.schedule') + ': ' + escapeHtml(pipe.schedule);
                        }
                        html += '</p></div>' +
                            '<div class="pipe-actions">' +
                                '<button class="toggle-switch ' + (pipe.enabled ? 'active' : '') + '" ' +
                                    'onclick="togglePipe(\\\'' + safeName + '\\\', ' + pipe.enabled + ')" ' +
                                    'title="' + actionBtn + '">' +
                                '</button>' +
                            '</div>' +
                        '</div>';
                    });
                    container.innerHTML = html;
                })
                .catch(function(err) {
                    document.getElementById('pipes-content').innerHTML =
                        '<div class="empty-state"><p>Error: ' + err + '</p></div>';
                });
        }

        function togglePipe(name, currentlyEnabled) {
            var action = currentlyEnabled ? 'disable' : 'enable';
            fetch('/api/screenpipe/pipes/' + encodeURIComponent(name) + '/' + action, {method: 'POST'})
                .then(function(r) { return r.json(); })
                .then(function(d) {
                    if (d.error) alert(d.error);
                    loadPipes();
                })
                .catch(function(err) { alert('Failed to toggle pipe: ' + err); });
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
                                '<div class="timeline-app">' + escapeHtml(ev.app_name) + (ev.window_title ? ' - ' + escapeHtml(ev.window_title) : '') + '</div>' +
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

        // ── PME Auto Cleaner ─────────────────────────────────────────
        var isPmeCleaning = false;

        function checkPmeStatus() {
            fetch('/api/pme/status')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    var indicator = document.getElementById('pme-status');
                    var info = document.getElementById('pme-info');
                    var card = document.getElementById('pme-main-card') || document.getElementById('pme-card');
                    var toggleBtn = document.getElementById('pme-toggle');
                    var btnClean = document.getElementById('btn-pme-clean');
                    var btnStart = document.getElementById('btn-pme-start');
                    var btnStop = document.getElementById('btn-pme-stop');

                    isPmeCleaning = data.running;
                    var autoEnabled = data.enabled;

                    // Update toggle button active state only if not disabled
                    if (toggleBtn && !toggleBtn.disabled) {
                        if (autoEnabled) {
                            toggleBtn.classList.add('active');
                        } else {
                            toggleBtn.classList.remove('active');
                        }
                    }

                    // Update Start/Stop buttons state if they exist (old UI support)
                    if (btnStart) btnStart.disabled = isPmeCleaning || autoEnabled;
                    if (btnStop) btnStop.disabled = isPmeCleaning || !autoEnabled;

                    if (isPmeCleaning) {
                        if (indicator) indicator.className = 'status-indicator running';
                        if (card) card.className = 'status-card active';
                        if (info) info.innerHTML = '⚡ ' + t('pme.status.running') + '<br><small>Phase: ' + (data.last_run_phase || 'all') + '</small>';
                        if (btnClean) btnClean.disabled = true;
                    } else {
                        var statusClass = '';
                        var statusText = '';
                        var indicatorClass = 'status-indicator stopped';
                        
                        if (!autoEnabled) {
                            statusText = '✗ ' + t('pme.status.disabled');
                            indicatorClass = 'status-indicator stopped';
                        } else {
                            statusClass = 'active';
                            indicatorClass = 'status-indicator running';
                            
                            if (data.last_run_status === 'success') {
                                var stats = data.schedule_state && data.schedule_state.last_ingest_stats ? data.schedule_state.last_ingest_stats : {};
                                var facts = stats.screen_facts || 0;
                                var obs = stats.screen_observations || 0;
                                var wkstreams = stats.window_workstream || 0;
                                
                                statusText = '✓ ' + t('pme.status.idle') + '<br><small>' + 
                                    (currentLang === 'zh' ? '上次清洗: ' : 'Last Clean: ') + (data.last_run_time || 'N/A') + '<br>' +
                                    'Facts: ' + facts + ' | Obs: ' + obs + ' | Wkstreams: ' + wkstreams + '</small>';
                            } else if (data.last_run_status === 'error') {
                                statusText = '✗ ' + t('pme.status.error') + '<br><small>' + (data.last_run_error || 'Unknown error').substring(0, 100) + '</small>';
                            } else {
                                var stats = data.schedule_state && data.schedule_state.last_ingest_stats ? data.schedule_state.last_ingest_stats : {};
                                var facts = stats.screen_facts || 0;
                                var obs = stats.screen_observations || 0;
                                var wkstreams = stats.window_workstream || 0;
                                statusText = t('pme.status.idle') + '<br><small>Facts: ' + facts + ' | Obs: ' + obs + ' | Wkstreams: ' + wkstreams + '</small>';
                            }
                        }

                        if (indicator) indicator.className = indicatorClass;
                        if (card) card.className = 'status-card ' + statusClass;
                        if (info) info.innerHTML = statusText;
                        if (btnClean) btnClean.disabled = false;
                    }
                });
        }

        function startServicePromise(statusUrl, startUrl) {
            return new Promise(function(resolve, reject) {
                // First check if already running
                fetch(statusUrl)
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        if (data.running) {
                            resolve(); // Already running!
                            return;
                        }
                        // Not running, trigger start
                        fetch(startUrl, {method: 'POST'})
                            .then(function() {
                                // Poll status
                                var attempts = 0;
                                var maxAttempts = 5;
                                var interval = setInterval(function() {
                                    attempts++;
                                    fetch(statusUrl)
                                        .then(function(r) { return r.json(); })
                                        .then(function(statusData) {
                                            if (statusData.running) {
                                                clearInterval(interval);
                                                resolve();
                                            } else if (attempts >= maxAttempts) {
                                                clearInterval(interval);
                                                reject(new Error((startUrl.indexOf('screenpipe') !== -1 ? 'Screenpipe' : 'OpenChronicle') + ' failed to start in time. Please check your TCC/system permissions.'));
                                            }
                                        })
                                        .catch(function(e) {
                                            if (attempts >= maxAttempts) {
                                                clearInterval(interval);
                                                reject(e);
                                            }
                                        });
                                }, 500);
                            })
                            .catch(reject);
                    })
                    .catch(reject);
            });
        }

        function togglePmeAutoClean() {
            var toggleBtn = document.getElementById('pme-toggle');
            if (!toggleBtn) return;
            var isCurrentlyEnabled = toggleBtn.classList.contains('active');
            
            if (isCurrentlyEnabled) {
                // Turn OFF
                toggleBtn.disabled = true;
                var info = document.getElementById('pme-info');
                if (info) info.innerHTML = currentLang === 'zh' ? '正在关闭 PME 自动清洗...' : 'Disabling PME Auto Cleaner...';
                
                fetch('/api/pme/stop', {method: 'POST'})
                    .then(function() {
                        if (info) info.innerHTML = currentLang === 'zh' ? '正在关闭依赖服务...' : 'Stopping dependent services...';
                        return Promise.all([
                            fetch('/api/screenpipe/stop', {method: 'POST'}),
                            fetch('/api/openchronicle/stop', {method: 'POST'})
                        ]);
                    })
                    .then(function() {
                        toggleBtn.disabled = false;
                        checkPmeStatus();
                        checkStatus();
                    })
                    .catch(function(err) {
                        toggleBtn.disabled = false;
                        alert('Failed to stop PME or dependencies: ' + err);
                        checkPmeStatus();
                        checkStatus();
                    });
            } else {
                // Turn ON
                toggleBtn.disabled = true;
                var info = document.getElementById('pme-info');
                if (info) info.innerHTML = currentLang === 'zh' ? '正在启动依赖服务...' : 'Starting dependent services...';
                
                startServicePromise('/api/screenpipe/status', '/api/screenpipe/start')
                    .then(function() {
                        if (info) info.innerHTML = currentLang === 'zh' ? '正在启动 OpenChronicle...' : 'Starting OpenChronicle...';
                        return startServicePromise('/api/openchronicle/status', '/api/openchronicle/start');
                    })
                    .then(function() {
                        if (info) info.innerHTML = currentLang === 'zh' ? '正在开启 PME 自动清洗...' : 'Enabling PME Auto Cleaner...';
                        return fetch('/api/pme/start', {method: 'POST'});
                    })
                    .then(function(r) { return r.json(); })
                    .then(function(d) {
                        toggleBtn.disabled = false;
                        if (d.success) {
                            checkPmeStatus();
                            checkStatus(); // Update other cards too
                        } else {
                            throw new Error(currentLang === 'zh' ? '开启 PME 自动清洗失败' : 'Failed to enable PME Auto Cleaner');
                        }
                    })
                    .catch(function(err) {
                        toggleBtn.disabled = false;
                        var errMsg = err.message || err;
                        alert(currentLang === 'zh' ? '启动失败: ' + errMsg : 'Startup failed: ' + errMsg);
                        fetch('/api/pme/stop', {method: 'POST'}).then(function() {
                            checkPmeStatus();
                            checkStatus();
                        });
                    });
            }
        }

        var manualCleanInterval = null;

        function triggerManualPmeClean() {
            var start = document.getElementById('manual-clean-start').value;
            var end = document.getElementById('manual-clean-end').value;
            var phase = document.getElementById('manual-clean-phase').value;
            
            var btn = document.getElementById('btn-trigger-manual-clean');
            var statusCard = document.getElementById('manual-clean-status-card');
            var indicator = document.getElementById('manual-clean-indicator');
            var statusTitle = document.getElementById('lbl-manual-status-title');
            var info = document.getElementById('manual-clean-info');
            
            if (btn) btn.disabled = true;
            if (statusCard) statusCard.style.display = 'block';
            if (indicator) indicator.className = 'status-indicator running';
            if (statusTitle) statusTitle.textContent = currentLang === 'zh' ? '清洗中...' : 'Cleaning...';
            if (info) info.innerHTML = currentLang === 'zh' ? '正在提交清洗任务...' : 'Submitting clean task...';
            
            fetch('/api/pme/clean', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    phase: phase,
                    start_time: start,
                    end_time: end
                })
            })
            .then(function(r) { return r.json(); })
            .then(function(d) {
                if (d.status === 'started') {
                    // Poll status
                    if (manualCleanInterval) clearInterval(manualCleanInterval);
                    manualCleanInterval = setInterval(pollManualCleanStatus, 1000);
                } else {
                    if (btn) btn.disabled = false;
                    if (indicator) indicator.className = 'status-indicator stopped';
                    if (statusTitle) statusTitle.textContent = currentLang === 'zh' ? '清洗服务繁忙' : 'Cleaner Busy';
                    if (info) info.innerHTML = d.message || (currentLang === 'zh' ? '已有其他清洗任务在执行中' : 'Another cleaner job is already running');
                }
            })
            .catch(function(err) {
                if (btn) btn.disabled = false;
                if (indicator) indicator.className = 'status-indicator stopped';
                if (statusTitle) statusTitle.textContent = currentLang === 'zh' ? '清洗错误' : 'Cleaning Error';
                if (info) info.innerHTML = 'Error: ' + err;
            });
        }

        function pollManualCleanStatus() {
            var btn = document.getElementById('btn-trigger-manual-clean');
            var indicator = document.getElementById('manual-clean-indicator');
            var statusTitle = document.getElementById('lbl-manual-status-title');
            var info = document.getElementById('manual-clean-info');
            
            fetch('/api/pme/status')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    if (data.running) {
                        if (statusTitle) statusTitle.textContent = currentLang === 'zh' ? '正在清洗...' : 'Cleaning...';
                        var phaseText = data.last_run_phase || 'all';
                        if (info) info.innerHTML = (currentLang === 'zh' ? '后台清洗任务正在运行。步骤: ' : 'Background cleaner is running. Phase: ') + phaseText;
                    } else {
                        // Finished
                        clearInterval(manualCleanInterval);
                        if (btn) btn.disabled = false;
                        
                        if (data.last_run_status === 'success') {
                            if (indicator) indicator.className = 'status-indicator running';
                            if (statusTitle) statusTitle.textContent = currentLang === 'zh' ? '清洗成功' : 'Cleaning Success';
                            if (info) info.innerHTML = formatCleaningStats(data.last_run_stats);
                        } else {
                            if (indicator) indicator.className = 'status-indicator stopped';
                            if (statusTitle) statusTitle.textContent = currentLang === 'zh' ? '清洗失败' : 'Cleaning Failed';
                            if (info) info.innerHTML = '<p style="color: #ef4444; font-weight: 600; margin: 0;">✗ ' + 
                                (currentLang === 'zh' ? '错误：' : 'Error: ') + escapeHtml(data.last_run_error || 'Unknown error') + '</p>';
                        }
                    }
                })
                .catch(function(err) {
                    clearInterval(manualCleanInterval);
                    if (btn) btn.disabled = false;
                    if (indicator) indicator.className = 'status-indicator stopped';
                    if (statusTitle) statusTitle.textContent = currentLang === 'zh' ? '轮询状态失败' : 'Polling Status Failed';
                    if (info) info.innerHTML = 'Error: ' + err;
                });
        }

        function formatCleaningStats(data) {
            if (!data) return '';
            var html = '<div style="margin-top: 10px; display: flex; flex-direction: column; gap: 8px;">';
            
            if (data.status === 'ok') {
                html += '<p style="color: #10b981; font-weight: 600; margin: 0;">✓ ' + (currentLang === 'zh' ? '清洗成功！' : 'Cleaning completed successfully!') + '</p>';
                if (data.phases && Object.keys(data.phases).length > 0) {
                    html += '<div style="border-top: 1px solid var(--border-color); padding-top: 8px; margin-top: 4px;">';
                    for (var phase in data.phases) {
                        var stats = data.phases[phase] || {};
                        var phaseName = phase;
                        if (phase === 'ingest') phaseName = currentLang === 'zh' ? '数据采集与过滤 (Ingest)' : 'Ingest & Filter';
                        else if (phase === 'fact_clustering') phaseName = currentLang === 'zh' ? '核心事实聚类 (Clustering)' : 'Fact Clustering';
                        else if (phase === 'observations') phaseName = currentLang === 'zh' ? '生成观察 (Observation)' : 'Observation Consolidation';
                        
                        html += '<div style="margin-bottom: 8px; border-bottom: 1px dashed var(--border-color); padding-bottom: 6px;">';
                        html += '<strong style="font-size: 13px; color: var(--text-primary);">' + phaseName + ':</strong>';
                        html += '<ul style="margin: 4px 0 0 16px; padding: 0; list-style-type: disc; font-size: 13px; color: var(--text-secondary);">';
                        
                        var hasItems = false;
                        for (var key in stats) {
                            hasItems = true;
                            var val = stats[key];
                            if (typeof val === 'object' && val !== null) {
                                val = JSON.stringify(val);
                            }
                            var label = key.replace(/_/g, ' ');
                            html += '<li>' + label + ': ' + val + '</li>';
                        }
                        if (!hasItems) {
                            html += '<li>' + (currentLang === 'zh' ? '无更新' : 'No updates') + '</li>';
                        }
                        html += '</ul></div>';
                    }
                    html += '</div>';
                } else {
                    html += '<p style="font-size: 13px; color: var(--text-secondary);">' + (currentLang === 'zh' ? '没有到期的清洗步骤，无需处理。' : 'No due phases to clean.') + '</p>';
                }
            } else {
                html += '<p style="color: #ef4444; font-weight: 600; margin: 0;">✗ ' + (currentLang === 'zh' ? '清洗失败' : 'Cleaning failed') + '</p>';
                if (data.message) {
                    html += '<p style="font-size: 13px; color: var(--text-secondary); margin: 4px 0 0 0;">' + escapeHtml(data.message) + '</p>';
                }
            }
            html += '</div>';
            return html;
        }

        function loadPmeConfig() {
            fetch('/api/pme/config')
                .then(function(r) { return r.json(); })
                .then(function(config) {
                    var db = config.database || {};
                    var sp = config.screenpipe || {};
                    var oc = config.openchronicle || {};
                    var sm = config.screen_memory || {};
                    var llm = config.model || {};
                    var emb = config.embedding || {};

                    document.getElementById('cfg-sp-db').value = db.screenpipe_db || '';
                    document.getElementById('cfg-oc-db').value = db.openchronicle_db || '';
                    document.getElementById('cfg-pme-db').value = db.cleaned_db || '';

                    document.getElementById('cfg-llm-provider').value = llm.provider || 'openai-codex';
                    document.getElementById('cfg-llm-model').value = llm.model || '';
                    document.getElementById('cfg-llm-url').value = llm.base_url || '';
                    document.getElementById('cfg-llm-temp').value = llm.temperature !== undefined ? llm.temperature : 0.2;
                    document.getElementById('cfg-llm-key').value = llm.api_key || '';

                    document.getElementById('cfg-emb-enabled').checked = !!emb.enabled;
                    document.getElementById('cfg-emb-provider').value = emb.provider || 'openai';
                    document.getElementById('cfg-emb-model').value = emb.model || '';
                    document.getElementById('cfg-emb-url').value = emb.base_url || '';
                    document.getElementById('cfg-emb-key-env').value = emb.api_key_env || 'EMBEDDING_API_KEY';
                    document.getElementById('cfg-emb-key').value = emb.api_key || '';
                    document.getElementById('cfg-emb-dimensions').value = emb.dimensions !== undefined ? emb.dimensions : 1536;
                    document.getElementById('cfg-emb-normalize').checked = emb.normalize !== false;

                    document.getElementById('pme-ingest-interval').value = sm.ingest_interval_minutes || 30;
                    document.getElementById('pme-cluster-interval').value = sm.fact_clustering_interval_hours || 2;
                    document.getElementById('pme-obs-interval').value = sm.observation_interval_hours || 24;

                    document.getElementById('cfg-sp-bin').value = sp.bin_path || '';
                    document.getElementById('cfg-oc-bin').value = oc.bin_path || '';
                    document.getElementById('cfg-sp-url').value = sp.api_url || '';
                    document.getElementById('cfg-sp-token').value = sp.api_token || '';
                    document.getElementById('cfg-sp-use-audio').checked = sp.use_audio !== false;
                })
                .catch(function(err) { console.error('Failed to load PME config:', err); });
        }

        function savePmeConfig() {
            var payload = {
                database: {
                    screenpipe_db: document.getElementById('cfg-sp-db').value,
                    openchronicle_db: document.getElementById('cfg-oc-db').value,
                    cleaned_db: document.getElementById('cfg-pme-db').value
                },
                model: {
                    provider: document.getElementById('cfg-llm-provider').value,
                    model: document.getElementById('cfg-llm-model').value,
                    base_url: document.getElementById('cfg-llm-url').value,
                    temperature: parseFloat(document.getElementById('cfg-llm-temp').value) || 0.2,
                    api_key: document.getElementById('cfg-llm-key').value
                },
                embedding: {
                    enabled: document.getElementById('cfg-emb-enabled').checked,
                    provider: document.getElementById('cfg-emb-provider').value,
                    model: document.getElementById('cfg-emb-model').value,
                    base_url: document.getElementById('cfg-emb-url').value,
                    api_key_env: document.getElementById('cfg-emb-key-env').value || 'EMBEDDING_API_KEY',
                    api_key: document.getElementById('cfg-emb-key').value,
                    dimensions: parseInt(document.getElementById('cfg-emb-dimensions').value) || 1536,
                    normalize: document.getElementById('cfg-emb-normalize').checked
                },
                screen_memory: {
                    ingest_interval_minutes: parseInt(document.getElementById('pme-ingest-interval').value) || 30,
                    fact_clustering_interval_hours: parseInt(document.getElementById('pme-cluster-interval').value) || 2,
                    observation_interval_hours: parseInt(document.getElementById('pme-obs-interval').value) || 24
                },
                screenpipe: {
                    bin_path: document.getElementById('cfg-sp-bin').value,
                    api_url: document.getElementById('cfg-sp-url').value,
                    api_token: document.getElementById('cfg-sp-token').value,
                    use_audio: document.getElementById('cfg-sp-use-audio').checked
                },
                openchronicle: {
                    bin_path: document.getElementById('cfg-oc-bin').value
                }
            };

            fetch('/api/pme/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(function(r) { return r.json(); })
            .then(function(d) {
                if (d.success) {
                    alert(currentLang === 'zh' ? '设置保存成功！' : 'Settings saved successfully!');
                } else {
                    var errorMsg = d.error || (currentLang === 'zh' ? '保存失败' : 'Failed to save settings');
                    alert((currentLang === 'zh' ? '保存失败: ' : 'Failed to save settings: ') + errorMsg);
                }
            })
            .catch(function(err) { alert('Failed to save configuration: ' + err); });
        }

        function loadStats() {
            // First update status labels for each section based on status check
            fetch('/api/screenpipe/status')
                .then(function(r) { return r.json(); })
                .then(function(d) {
                    var el = document.getElementById('stat-sp-status');
                    if (el) {
                        el.textContent = d.running ? (currentLang === 'zh' ? '运行中' : 'Running') : (currentLang === 'zh' ? '已停止' : 'Stopped');
                        el.style.background = d.running ? 'rgba(16, 185, 129, 0.1)' : 'var(--border-color)';
                        el.style.color = d.running ? '#10b981' : 'var(--text-secondary)';
                    }
                });
            fetch('/api/openchronicle/status')
                .then(function(r) { return r.json(); })
                .then(function(d) {
                    var el = document.getElementById('stat-oc-status');
                    if (el) {
                        el.textContent = d.running ? (currentLang === 'zh' ? '运行中' : 'Running') : (currentLang === 'zh' ? '已停止' : 'Stopped');
                        el.style.background = d.running ? 'rgba(16, 185, 129, 0.1)' : 'var(--border-color)';
                        el.style.color = d.running ? '#10b981' : 'var(--text-secondary)';
                    }
                });
            fetch('/api/pme/status')
                .then(function(r) { return r.json(); })
                .then(function(d) {
                    var el = document.getElementById('stat-pme-status');
                    if (el) {
                        el.textContent = d.enabled ? (currentLang === 'zh' ? '已启用' : 'Enabled') : (currentLang === 'zh' ? '已禁用' : 'Disabled');
                        el.style.background = d.enabled ? 'rgba(16, 185, 129, 0.1)' : 'var(--border-color)';
                        el.style.color = d.enabled ? '#10b981' : 'var(--text-secondary)';
                    }
                });

            // Fetch actual database statistics
            fetch('/api/stats/summary')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    // Update Screenpipe stats
                    var sp = data.screenpipe || {};
                    document.getElementById('stat-sp-total').textContent = sp.exists ? (sp.total_captures !== undefined ? sp.total_captures : '-') : 'N/A';
                    document.getElementById('stat-sp-daily').textContent = sp.exists ? (sp.daily_captures !== undefined ? sp.daily_captures : '-') : 'N/A';
                    document.getElementById('stat-sp-weekly').textContent = sp.exists ? (sp.weekly_captures !== undefined ? sp.weekly_captures : '-') : 'N/A';
                    document.getElementById('stat-sp-storage').textContent = sp.exists ? (sp.storage_mb !== undefined ? sp.storage_mb : '-') : 'N/A';

                    // Update OpenChronicle stats
                    var oc = data.openchronicle || {};
                    document.getElementById('stat-oc-total').textContent = oc.exists ? (oc.total_captures !== undefined ? oc.total_captures : '-') : 'N/A';
                    document.getElementById('stat-oc-daily').textContent = oc.exists ? (oc.daily_captures !== undefined ? oc.daily_captures : '-') : 'N/A';
                    document.getElementById('stat-oc-weekly').textContent = oc.exists ? (oc.weekly_captures !== undefined ? oc.weekly_captures : '-') : 'N/A';
                    document.getElementById('stat-oc-storage').textContent = oc.exists ? (oc.storage_mb !== undefined ? oc.storage_mb : '-') : 'N/A';

                    // Update PME stats
                    var pme = data.pme || {};
                    document.getElementById('stat-pme-total').textContent = pme.exists ? (pme.total_captures !== undefined ? pme.total_captures : '-') : 'N/A';
                    document.getElementById('stat-pme-daily').textContent = pme.exists ? (pme.daily_captures !== undefined ? pme.daily_captures : '-') : 'N/A';
                    document.getElementById('stat-pme-weekly').textContent = pme.exists ? (pme.weekly_captures !== undefined ? pme.weekly_captures : '-') : 'N/A';
                    document.getElementById('stat-pme-storage').textContent = pme.exists ? (pme.storage_mb !== undefined ? pme.storage_mb : '-') : 'N/A';
                })
                .catch(function(err) { console.error('Failed to load stats summary:', err); });
        }

        // ── Initialize ──────────────────────────────────────────────
        function init() {
            applyTheme();
            applyI18n();
            var langBtn = document.getElementById('lang-toggle');
            if (langBtn) langBtn.textContent = currentLang === 'en' ? 'EN' : '中文';
            var dateInput = document.getElementById('timeline-date');
            if (dateInput) dateInput.value = new Date().toISOString().split('T')[0];
            checkStatus();
            loadHeatmap();
            loadPmeConfig();
            checkPmeStatus();
            setInterval(checkStatus, 10000);
            setInterval(checkPmeStatus, 10000);
            setInterval(loadHeatmap, 60000);
        }

        init();
    </script>
</body>
</html>"""
