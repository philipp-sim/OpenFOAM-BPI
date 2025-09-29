
# ===== REFRES =====
REFRESH_INTERVAL = 5  
# ==================

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import re
import numpy as np
from pathlib import Path
import plotly.io as pio
import sys
import os
import webbrowser
import json
import time
import http.server
import socketserver
import threading
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as patches

# Terminal/Command Line Setup für bessere Plots
plt.style.use('seaborn-v0_8')
# Matplotlib Backend für keine automatischen Fenster
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import plotly.offline as pyo

# Automatische Renderer-Erkennung
def setup_plotly_renderer():
    try:
        from IPython import get_ipython
        if get_ipython() is not None:
            pio.renderers.default = "notebook"
            print("Jupyter/IPython Umgebung erkannt - Plots werden inline angezeigt")
            return "jupyter"
    except ImportError:
        pass
    
    # Terminal/Kommandozeile Setup - KEINE automatischen Browser-Fenster
    pio.renderers.default = "json"  
    print("Terminal-Modus - Keine automatischen Plot-Fenster")
    return "terminal"

# Renderer konfigurieren
ENVIRONMENT = setup_plotly_renderer()

def show_plot(fig, title="Plot"):
    """Plot-Anzeige - nur auf Anfrage, keine automatischen Fenster"""
    return False  # Keine automatischen Plots
print("Libraries erfolgreich importiert!")

# Load and Parse OpenFOAM Data File
def parse_openfoam_data(file_path):
    """
    Parst die OpenFOAM Data-Datei und extrahiert Zeitschritt- und alle relevanten Daten
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Regex Pattern für alle Datentypen
        timestep_pattern = r'Timestep\s+([\d\.]+)\s+\|'
        cell_count_pattern = r'Cells\s+(\d+)'
        mass_imbalance_pattern = r'Mass imbalance:.*?\(([-\d\.]+)\s*%\)'
        volume_diff_pattern = r'Volume diff:.*?\(([-\d\.]+)\s*%\)'
        net_power_loss_pattern = r'Net power loss:\s+([-\d\.]+)\s+W'
        net_energy_loss_pattern = r'Net energy loss:\s+([-\d\.]+)\s+J'
        outflow_volume_pattern = r'Outflow volume:\s+([-\d\.]+)\s+m³/s'
        
        # Finde alle Datenblöcke
        blocks = content.split('----------------------------------------')
        
        timesteps = []
        cell_counts = []
        mass_imbalances = []
        volume_diffs = []
        net_power_losses = []
        net_energy_losses = []
        outflow_volumes = []
        
        for block in blocks:
            if 'Timestep' not in block:
                continue
                
            try:
                # Extrahiere Timestep
                ts_match = re.search(timestep_pattern, block)
                if not ts_match:
                    continue
                timestep = float(ts_match.group(1))
                
                # Extrahiere Cell Count
                cc_match = re.search(cell_count_pattern, block)
                if cc_match:
                    cell_count = int(cc_match.group(1))
                else:
                    cell_count = 0
                
                # Extrahiere Mass imbalance (%)
                mi_match = re.search(mass_imbalance_pattern, block)
                if mi_match:
                    mass_imbalance = float(mi_match.group(1))
                else:
                    mass_imbalance = 0.0
                
                # Extrahiere Volume diff (%)
                vd_match = re.search(volume_diff_pattern, block)
                if vd_match:
                    volume_diff = float(vd_match.group(1))
                else:
                    volume_diff = 0.0
                
                # Extrahiere Net power loss (W)
                npl_match = re.search(net_power_loss_pattern, block)
                if npl_match:
                    net_power_loss = float(npl_match.group(1))
                else:
                    net_power_loss = 0.0
                
                # Extrahiere Net energy loss (J)
                nel_match = re.search(net_energy_loss_pattern, block)
                if nel_match:
                    net_energy_loss = float(nel_match.group(1))
                else:
                    net_energy_loss = 0.0
                
                # Extrahiere Outflow volume (m³/s)
                ofv_match = re.search(outflow_volume_pattern, block)
                if ofv_match:
                    outflow_volume = float(ofv_match.group(1))
                else:
                    outflow_volume = 0.0
                
                # Alle Werte hinzufügen
                timesteps.append(timestep)
                cell_counts.append(cell_count)
                mass_imbalances.append(mass_imbalance)
                volume_diffs.append(volume_diff)
                net_power_losses.append(net_power_loss)
                net_energy_losses.append(net_energy_loss)
                outflow_volumes.append(outflow_volume)
                
            except (ValueError, AttributeError) as e:
                continue
        
        #print(f"Erfolgreich {len(timesteps)} Datenpunkte geparst!")
        #print(f"Zeitschritt-Bereich: {min(timesteps):.3f} - {max(timesteps):.3f}")
        
        return timesteps, cell_counts, mass_imbalances, volume_diffs, net_power_losses, net_energy_losses, outflow_volumes
        
    except FileNotFoundError:
        print(f"Datei {file_path} nicht gefunden!")
        return [], [], [], [], [], [], []
    except Exception as e:
        print(f"Fehler beim Parsen der Datei: {e}")
        return [], [], [], [], [], [], []

# Pfad zur OpenFOAM Data-Datei
data_file_path = "/Users/philipp.simlinger/openFOAM/work/validation/V03/postProcess/EnergyLoss/Data"

# Daten parsen
timesteps, cell_counts, mass_imbalances, volume_diffs, net_power_losses, net_energy_losses, outflow_volumes = parse_openfoam_data(data_file_path)

# Extract Time Series Data
if timesteps and mass_imbalances:
    # DataFrame erstellen mit allen Datentypen
    df = pd.DataFrame({
        'Timestep': timesteps,
        'Cell_Count': cell_counts,
        'Mass_Imbalance_Percent': mass_imbalances,
        'Volume_Diff_Percent': volume_diffs,
        'Net_Power_Loss_W': net_power_losses,
        'Net_Energy_Loss_J': net_energy_losses,
        'Outflow_Volume_m3s': outflow_volumes
    })
    
    # Daten sortieren nach Zeitschritt
    df = df.sort_values('Timestep').reset_index(drop=True)
    
    # Erste und letzte Datenpunkte anzeigen
    print("Erste 5 Datenpunkte:")
    print(df.head())
    print("\nLetzte 5 Datenpunkte:")
    print(df.tail())
    
    # Grundlegende Statistiken
    #print("\nGrundlegende Statistiken:")
    #print(df.describe())
    
else:
    print("Keine Daten zum Verarbeiten gefunden!")
    df = pd.DataFrame()
    
# Create Interactive Plot
if not df.empty:
    # Plotly interaktiver Plot
    fig = go.Figure()
    
    # Hauptlinie hinzufügen
    fig.add_trace(go.Scatter(
        x=df['Timestep'],
        y=df['Mass_Imbalance_Percent'],
        mode='lines+markers',
        name='Mass Imbalance',
        line=dict(color='blue', width=2),
        marker=dict(size=4),
        hovertemplate='<b>Timestep:</b> %{x:.3f}<br>' +
                     '<b>Mass Imbalance:</b> %{y:.3f}%<br>' +
                     '<extra></extra>'
    ))
    
    # Layout konfigurieren
    fig.update_layout(
        title='OpenFOAM Mass Imbalance über Zeit',
        xaxis_title='Timestep',
        yaxis_title='Mass Imbalance (%)',
        hovermode='x unified',
        showlegend=True,
        template='plotly_white',
        width=1000,
        height=600
    )
    
    # Grid hinzufügen
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    
    
else:
    print("Keine Daten zum Plotten vorhanden!")

# Data Analysis and Statistics
if not df.empty:
    # Statistische Analyse
    mean_imbalance = df['Mass_Imbalance_Percent'].mean()
    std_imbalance = df['Mass_Imbalance_Percent'].std()
    min_imbalance = df['Mass_Imbalance_Percent'].min()
    max_imbalance = df['Mass_Imbalance_Percent'].max()
    
    print("=== STATISTISCHE ANALYSE ===")
    print(f"Mittelwert:           {mean_imbalance:.4f}%")
    print(f"Standardabweichung:   {std_imbalance:.4f}%")
    print(f"Minimum:              {min_imbalance:.4f}%")
    print(f"Maximum:              {max_imbalance:.4f}%")
    print(f"Bereich:              {max_imbalance - min_imbalance:.4f}%")
    
    # Daten als CSV speichern
    output_file = "mass_imbalance_analysis.csv"
    df.to_csv(output_file, index=False)
    #print(f"\nDaten gespeichert in: {output_file}")

    
else:
    print("Keine Daten für die Analyse verfügbar!")

# Live Monitoring Setup
import time
import threading
from datetime import datetime

class LiveMassImbalanceMonitor:
    """
    Klasse für Live-Monitoring mit automatischen Updates
    """
    def __init__(self, data_file_path, update_interval=REFRESH_INTERVAL):
        self.data_file_path = data_file_path
        self.update_interval = update_interval
        self.is_running = False
        self.last_data_count = 0
        self.html_file = "live_monitor.html"
        self.data_file_json = "live_data.json"
        self.browser_opened = False
        self.http_server = None
        self.server_port = None
        
    def create_html_file(self):
        """Erstellt eine HTML-Datei mit Auto-Refresh und mehreren Graphen"""
        html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenFOAM Live Monitor</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 20px; }
        .status-header { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 20px; }
        .status-box { background: #e3f2fd; padding: 10px; border-radius: 5px; text-align: center; }
        .status-value { font-size: 18px; font-weight: bold; color: #1976d2; }
        .status-label { color: #666; font-size: 12px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; margin-bottom: 20px; }
        .metric-box { background: #f8f9fa; padding: 10px; border-radius: 5px; text-align: center; }
        .metric-current { font-size: 16px; font-weight: bold; margin-bottom: 5px; }
        .metric-mean { font-size: 14px; opacity: 0.8; }
        .metric-label { color: #666; font-size: 11px; margin-top: 5px; }
        .metric-mass .metric-current { color: blue; }
        .metric-volume .metric-current { color: green; }
        .metric-power .metric-current { color: orange; }
        .metric-energy .metric-current { color: purple; }
        .metric-cumulative .metric-current { color: darkred; }
        .metric-flow .metric-current { color: teal; }
        .plots-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        .plot-container { background: #f8f9fa; padding: 15px; border-radius: 8px; }
        .plot { width: 100%; height: 350px; }
        .plot-full-width { margin-bottom: 20px; }
        .plot-full-width .plot-container { background: #f8f9fa; padding: 15px; border-radius: 8px; }
        .plot-full-width .plot { width: 100%; height: 400px; }
        .plot-title { font-size: 16px; font-weight: bold; margin-bottom: 10px; text-align: center; color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> OpenFOAM Live Monitor</h1>
            <p id="last-update">Lade Daten... | Cells --</p>
        </div>
        
        <div class="status-header">
            <div class="status-box">
                <div class="status-value" id="update-count">--</div>
                <div class="status-label">Update Nr.</div>
            </div>
            <div class="status-box">
                <div class="status-value" id="data-points">--</div>
                <div class="status-label">Datenpunkte</div>
            </div>
            <div class="status-box">
                <div class="status-value" id="timestep">--</div>
                <div class="status-label">Aktueller Zeitschritt</div>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-box metric-mass">
                <div class="metric-current" id="current-mass-imbalance">--</div>
                <div class="metric-mean" id="mean-mass-imbalance">Ø --</div>
                <div class="metric-label">Mass Imbalance (%)</div>
            </div>
            <div class="metric-box metric-volume">
                <div class="metric-current" id="current-volume-diff">--</div>
                <div class="metric-mean" id="mean-volume-diff">Ø --</div>
                <div class="metric-label">Volume Diff (%)</div>
            </div>
            <div class="metric-box metric-flow">
                <div class="metric-current" id="current-outflow-volume">--</div>
                <div class="metric-mean" id="mean-outflow-volume">Ø --</div>
                <div class="metric-label">Flow Volume (m³/s)</div>
            </div>
            <div class="metric-box metric-power">
                <div class="metric-current" id="current-power-loss">--</div>
                <div class="metric-mean" id="mean-power-loss">Ø --</div>
                <div class="metric-label">Net Power Loss (W)</div>
            </div>
            <div class="metric-box metric-energy">
                <div class="metric-current" id="current-energy-loss">--</div>
                <div class="metric-mean" id="mean-energy-loss">Ø --</div>
                <div class="metric-label">Net Energy Loss (J)</div>
            </div>
            <div class="metric-box metric-cumulative">
                <div class="metric-current" id="cumulative-energy-loss">--</div>
                <div class="metric-mean" id="mean-cumulative-energy-loss">Ø --</div>
                <div class="metric-label">Kumulierter Energy Loss (J)</div>
            </div>
        </div>
        
        <div class="plots-grid">
            <div class="plot-container">
                <div class="plot-title">Mass Imbalance</div>
                <div id="plot-mass-imbalance" class="plot"></div>
            </div>
            
            <div class="plot-container">
                <div class="plot-title">Volume Diff</div>
                <div id="plot-volume-diff" class="plot"></div>
            </div>
            
            <div class="plot-container">
                <div class="plot-title">Net Power Loss</div>
                <div id="plot-power-loss" class="plot"></div>
            </div>
            
            <div class="plot-container">
                <div class="plot-title">Net Energy Loss</div>
                <div id="plot-energy-loss" class="plot"></div>
            </div>
        </div>
        
        <div class="plots-grid">
            <div class="plot-container">
                <div class="plot-title">Kumulierter Energy Loss</div>
                <div id="plot-cumulative-energy-loss" class="plot"></div>
            </div>
            
            <div class="plot-container">
                <div class="plot-title">Flow Volume</div>
                <div id="plot-flow-volume" class="plot"></div>
            </div>
        </div>
    </div>

    <script>
        let updateCount = 0;
        
        function createPlot(elementId, data, yField, yTitle, color, currentValue) {
            const trace = {
                x: data.map(d => d.timestep),
                y: data.map(d => d[yField]),
                type: 'scatter',
                mode: 'lines+markers',
                name: yTitle,
                line: { color: color, width: 2 },
                marker: { size: 3 }
            };
            
            const currentPoint = {
                x: [data[data.length - 1].timestep],
                y: [currentValue],
                type: 'scatter',
                mode: 'markers',
                name: 'Aktuell',
                marker: { size: 8, color: 'red', symbol: 'diamond' }
            };
            
            const layout = {
                xaxis: { title: 'Timestep' },
                yaxis: { title: yTitle },
                hovermode: 'x unified',
                showlegend: true,
                margin: { l: 60, r: 20, t: 20, b: 40 }
            };
            
            Plotly.newPlot(elementId, [trace, currentPoint], layout);
        }
        
        function loadData() {
            fetch('live_data.json?' + new Date().getTime())
                .then(response => response.json())
                .then(data => {
                    updateCount++;
                    
                    if (data.length > 0) {
                        const currentData = data[data.length - 1];
                        
                        document.getElementById('last-update').textContent = 
                            'Letztes Update: ' + new Date().toLocaleTimeString() + ' | Weighted Cells ' + currentData.cell_count;
                        document.getElementById('update-count').textContent = updateCount;
                        
                        // Mittelwerte berechnen
                        const meanMassImbalance = data.reduce((sum, d) => sum + d.mass_imbalance, 0) / data.length;
                        const meanVolumeDiff = data.reduce((sum, d) => sum + d.volume_diff, 0) / data.length;
                        const meanPowerLoss = data.reduce((sum, d) => sum + d.power_loss, 0) / data.length;
                        const meanEnergyLoss = data.reduce((sum, d) => sum + d.energy_loss, 0) / data.length;
                        const meanOutflowVolume = data.reduce((sum, d) => sum + d.outflow_volume, 0) / data.length;
                        
                        // Rate der Zunahme für kumulative Werte berechnen
                        let rateCumulativeEnergyLoss = 0;
                        if (data.length > 1) {
                            const firstValue = data[0].cumulative_energy_loss;
                            const lastValue = data[data.length - 1].cumulative_energy_loss;
                            const timeSpan = data.length - 1; // Anzahl der Zeitschritte
                            
                            rateCumulativeEnergyLoss = (lastValue - firstValue) / timeSpan;
                        }
                        
                        // Status Header aktualisieren
                        document.getElementById('data-points').textContent = data.length;
                        document.getElementById('timestep').textContent = currentData.timestep.toFixed(3);
                        
                        // Aktuelle Werte und Mittelwerte anzeigen
                        document.getElementById('current-mass-imbalance').textContent = currentData.mass_imbalance.toFixed(4);
                        document.getElementById('mean-mass-imbalance').textContent = 'Ø ' + meanMassImbalance.toFixed(4);
                        
                        document.getElementById('current-volume-diff').textContent = currentData.volume_diff.toFixed(4);
                        document.getElementById('mean-volume-diff').textContent = 'Ø ' + meanVolumeDiff.toFixed(4);
                        
                        document.getElementById('current-power-loss').textContent = currentData.power_loss.toFixed(2);
                        document.getElementById('mean-power-loss').textContent = 'Ø ' + meanPowerLoss.toFixed(2);
                        
                        document.getElementById('current-energy-loss').textContent = currentData.energy_loss.toFixed(4);
                        document.getElementById('mean-energy-loss').textContent = 'Ø ' + meanEnergyLoss.toFixed(4);
                        
                        document.getElementById('cumulative-energy-loss').textContent = currentData.cumulative_energy_loss.toFixed(2);
                        document.getElementById('mean-cumulative-energy-loss').textContent = '▲ ' + rateCumulativeEnergyLoss.toFixed(2) + ' J/Iteration';

                        document.getElementById('current-outflow-volume').textContent = currentData.outflow_volume.toFixed(6);
                        document.getElementById('mean-outflow-volume').textContent = 'Ø ' + meanOutflowVolume.toFixed(6);

                        // Plots erstellen
                        createPlot('plot-mass-imbalance', data, 'mass_imbalance', 'Mass Imbalance (%)', 'blue', currentData.mass_imbalance);
                        createPlot('plot-volume-diff', data, 'volume_diff', 'Volume Diff (%)', 'green', currentData.volume_diff);
                        createPlot('plot-power-loss', data, 'power_loss', 'Net Power Loss (W)', 'orange', currentData.power_loss);
                        createPlot('plot-energy-loss', data, 'energy_loss', 'Net Energy Loss (J)', 'purple', currentData.energy_loss);
                        createPlot('plot-cumulative-energy-loss', data, 'cumulative_energy_loss', 'Kumulierter Energy Loss (J)', 'darkred', currentData.cumulative_energy_loss);
                        createPlot('plot-flow-volume', data, 'outflow_volume', 'Flow Volume (m³/s)', 'teal', currentData.outflow_volume);
                    }
                })
                .catch(error => {
                    console.error('Fehler beim Laden der Daten:', error);
                    document.getElementById('update-count').textContent = 'Fehler';
                });
        }
        
        setInterval(loadData, REFRESH_INTERVAL_MS);
        loadData();
    </script>
</body>
</html>"""
        
        # Replace the placeholder with the actual refresh interval
        html_content = html_content.replace('REFRESH_INTERVAL_MS', str(REFRESH_INTERVAL * 1000))
        
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
    def update_data_file(self, timesteps, cell_counts, mass_imbalances, volume_diffs, net_power_losses, net_energy_losses, outflow_volumes):
        """Aktualisiert die JSON-Datei mit allen neuen Daten"""
        data = []
        cumulative_energy_loss = 0.0
        
        for ts, cc, mi, vd, pl, el, ov in zip(timesteps, cell_counts, mass_imbalances, volume_diffs, net_power_losses, net_energy_losses, outflow_volumes):
            cumulative_energy_loss += el  # Aufsummieren der Energy Loss
            data.append({
                'timestep': float(ts),
                'cell_count': int(cc),
                'mass_imbalance': float(mi),
                'volume_diff': float(vd),
                'power_loss': float(pl),
                'energy_loss': float(el),
                'cumulative_energy_loss': float(cumulative_energy_loss),
                'outflow_volume': float(ov)
            })
        
        with open(self.data_file_json, 'w') as f:
            json.dump(data, f)
    
    def start_monitoring(self, mode='console'):
        """Startet die Live-Überwachung mit verschiedenen Modi"""
        print("Starte Live-Monitoring des OpenFOAM Mass Imbalance...")
        print(f"Datei: {self.data_file_path}")
        print(f"Update-Intervall: {self.update_interval} Sekunden")
        print(f"Modus: {mode}")
        print("Drücke Ctrl+C zum Beenden\n")
        
        self.is_running = True
        
        if mode == 'browser':
            self.create_html_file()
            print(f"HTML-Dashboard erstellt: {self.html_file}")
            # Start HTTP server for local file access
            import http.server
            import socketserver
            import threading
            import socket
            
            def find_free_port(start_port=8000):
                """Findet einen freien Port"""
                for port in range(start_port, start_port + 10):
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.bind(('', port))
                            return port
                    except OSError:
                        continue
                return None
            
            PORT = find_free_port()
            if PORT is None:
                print("Fehler: Kein freier Port gefunden. Verwende file:// URL.")
                browser_url = f'file://{os.path.abspath(self.html_file)}'
            else:
                browser_url = f'http://localhost:{PORT}/{self.html_file}'
                
                def start_server():
                    Handler = http.server.SimpleHTTPRequestHandler
                    Handler.log_message = lambda self, format, *args: None  # Suppress logs
                    try:
                        with socketserver.TCPServer(("", PORT), Handler) as httpd:
                            print(f"HTTP Server läuft auf http://localhost:{PORT}")
                            httpd.serve_forever()
                    except Exception as e:
                        print(f"Server-Fehler: {e}")
                
                # Start server in background thread
                server_thread = threading.Thread(target=start_server, daemon=True)
                server_thread.start()
                
                # Wait a moment for server to start
                import time
                time.sleep(1)
        
        try:
            while self.is_running:
                # Daten laden
                timesteps, cell_counts, mass_imbalances, volume_diffs, net_power_losses, net_energy_losses, outflow_volumes = parse_openfoam_data(self.data_file_path)
                
                if len(mass_imbalances) > 0:
                    current_count = len(mass_imbalances)
                    
                    if current_count != self.last_data_count:
                        current_time = time.strftime("%H:%M:%S")
                        current_timestep = timesteps[-1]
                        current_cell_count = cell_counts[-1]
                        current_mass_imbalance = mass_imbalances[-1]
                        current_volume_diff = volume_diffs[-1]
                        current_power_loss = net_power_losses[-1]
                        current_energy_loss = net_energy_losses[-1]
                        
                        if mode == 'console':
                            print(f"[{current_time}] Timestep: {current_timestep:.3f}, Cells: {current_cell_count}, "
                                  f"Mass Imbalance: {current_mass_imbalance:.4f}%, "
                                  f"Volume Diff: {current_volume_diff:.4f}%, "
                                  f"Power Loss: {current_power_loss:.2f}W, "
                                  f"Energy Loss: {current_energy_loss:.4f}J, "
                                  f"Datenpunkte: {current_count}")
                        
                        elif mode == 'browser':
                            # JSON-Datei aktualisieren
                            self.update_data_file(timesteps, cell_counts, mass_imbalances, volume_diffs, net_power_losses, net_energy_losses, outflow_volumes)
                            self.update_data_file(timesteps, cell_counts, mass_imbalances, volume_diffs, net_power_losses, net_energy_losses, outflow_volumes)
                            
                            # Browser nur beim ersten Mal öffnen
                            if not self.browser_opened:
                                webbrowser.open(browser_url)
                                self.browser_opened = True
                                print(f"Browser geöffnet mit Dashboard: {browser_url}")
                            
                            """
                            print(f"[{current_time}] Dashboard aktualisiert - "
                                  f"Timestep: {current_timestep:.3f}, "
                                  f"Wert: {current_value:.4f}%, "
                                  f"Datenpunkte: {current_count}")
                            """
                        
                        self.last_data_count = current_count
                    
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring gestoppt.")
            self.is_running = False
        
    def update_plot(self):
        """Einmaliges Update des Plots"""
        timesteps_new, cell_counts_new, mass_imbalances_new, volume_diffs_new, net_power_losses_new, net_energy_losses_new, outflow_volumes_new = parse_openfoam_data(self.data_file_path)
        
        if timesteps_new and mass_imbalances_new:
            df_new = pd.DataFrame({
                'Timestep': timesteps_new,
                'Cell_Count': cell_counts_new,
                'Mass_Imbalance_Percent': mass_imbalances_new,
                'Volume_Diff_Percent': volume_diffs_new,
                'Net_Power_Loss_W': net_power_losses_new,
                'Net_Energy_Loss_J': net_energy_losses_new,
                'Outflow_Volume_m3s': outflow_volumes_new
            }).sort_values('Timestep')
            
            # Statistiken berechnen
            current_cell_count = df_new.iloc[-1]['Cell_Count']
            current_mass_imbalance = df_new.iloc[-1]['Mass_Imbalance_Percent']
            current_volume_diff = df_new.iloc[-1]['Volume_Diff_Percent']
            current_power_loss = df_new.iloc[-1]['Net_Power_Loss_W']
            current_energy_loss = df_new.iloc[-1]['Net_Energy_Loss_J']
            current_timestep = df_new.iloc[-1]['Timestep']
            
            # Live-Monitoring: Nur Konsolen-Ausgabe, keine Plots
            print(f"Live-Update: Timestep {current_timestep:.3f}, Cells {current_cell_count}, "
                  f"Mass Imbalance: {current_mass_imbalance:.4f}%, "
                  f"Volume Diff: {current_volume_diff:.4f}%, "
                  f"Power Loss: {current_power_loss:.2f}W, "
                  f"Energy Loss: {current_energy_loss:.4f}J")
            
            # Neue Daten erkennen
            if len(df_new) > self.last_data_count:
                new_points = len(df_new) - self.last_data_count
                print(f"🔄 {new_points} neue Datenpunkte erkannt!")
                self.last_data_count = len(df_new)
            
            return True
        return False
    
    def start_auto_monitoring(self):
        """Startet automatisches Monitoring"""
        if self.is_running:
            print("Monitoring läuft bereits!")
            return
            
        self.is_running = True
        print(f"🚀 Automatisches Monitoring gestartet (Update alle {self.update_interval}s)")
        print("Drücken Sie Ctrl+C zum Beenden")
        
        try:
            while self.is_running:
                print(f"\n📊 Update um {datetime.now().strftime('%H:%M:%S')}")
                self.update_plot()
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring gestoppt")
            self.is_running = False
    
    def stop_monitoring(self):
        """Stoppt das Monitoring"""
        self.is_running = False
        print("Monitoring wird gestoppt...")
        
    def create_pdf_snapshot(self, output_filename=None):
        """
        Erstellt einen PDF-Snapshot der aktuellen Monitor-Ansicht
        
        Parameters:
        -----------
        output_filename : str, optional
            Name der PDF-Datei. Wenn nicht angegeben, wird automatisch ein Name generiert.
        
        Returns:
        --------
        str : Pfad zur erstellten PDF-Datei
        """
        return create_pdf_report(self.data_file_path, output_filename)

def create_pdf_report(data_file_path=None, output_filename=None):
    """
    Erstellt einen umfassenden PDF-Report mit allen aktuellen Daten und Plots
    
    Parameters:
    -----------
    data_file_path : str, optional
        Pfad zur OpenFOAM Datendatei. Wenn nicht angegeben, wird der Standard verwendet.
    output_filename : str, optional
        Name der PDF-Datei. Wenn nicht angegeben, wird automatisch ein Name generiert.
    
    Returns:
    --------
    str : Pfad zur erstellten PDF-Datei
    """
    
    if data_file_path is None:
        data_file_path = "/Users/philipp.simlinger/openFOAM/work/validation/V03/postProcess/EnergyLoss/Data"
    
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"OpenFOAM_Monitor_Report_{timestamp}.pdf"
    
    print(f"📄 Erstelle PDF-Report: {output_filename}")
    
    # Aktuelle Daten laden
    timesteps, cell_counts, mass_imbalances, volume_diffs, net_power_losses, net_energy_losses, outflow_volumes = parse_openfoam_data(data_file_path)
    
    if not timesteps:
        print("❌ Keine Daten gefunden. PDF kann nicht erstellt werden.")
        return None
    
    # DataFrame erstellen
    df = pd.DataFrame({
        'Timestep': timesteps,
        'Cell_Count': cell_counts,
        'Mass_Imbalance_Percent': mass_imbalances,
        'Volume_Diff_Percent': volume_diffs,
        'Net_Power_Loss_W': net_power_losses,
        'Net_Energy_Loss_J': net_energy_losses,
        'Outflow_Volume_m3s': outflow_volumes
    }).sort_values('Timestep')
    
    # Kumulative Werte berechnen
    df['Cumulative_Energy_Loss_J'] = df['Net_Energy_Loss_J'].cumsum()
    
    # Statistiken berechnen
    stats = {
        'total_data_points': len(df),
        'time_range': (df['Timestep'].min(), df['Timestep'].max()),
        'cell_count': df['Cell_Count'].iloc[-1] if not df.empty else 0,
        'mass_imbalance': {
            'current': df['Mass_Imbalance_Percent'].iloc[-1],
            'mean': df['Mass_Imbalance_Percent'].mean(),
            'std': df['Mass_Imbalance_Percent'].std(),
            'min': df['Mass_Imbalance_Percent'].min(),
            'max': df['Mass_Imbalance_Percent'].max()
        },
        'volume_diff': {
            'current': df['Volume_Diff_Percent'].iloc[-1],
            'mean': df['Volume_Diff_Percent'].mean(),
            'std': df['Volume_Diff_Percent'].std(),
            'min': df['Volume_Diff_Percent'].min(),
            'max': df['Volume_Diff_Percent'].max()
        },
        'power_loss': {
            'current': df['Net_Power_Loss_W'].iloc[-1],
            'mean': df['Net_Power_Loss_W'].mean(),
            'std': df['Net_Power_Loss_W'].std(),
            'min': df['Net_Power_Loss_W'].min(),
            'max': df['Net_Power_Loss_W'].max()
        },
        'energy_loss': {
            'current': df['Net_Energy_Loss_J'].iloc[-1],
            'mean': df['Net_Energy_Loss_J'].mean(),
            'std': df['Net_Energy_Loss_J'].std(),
            'min': df['Net_Energy_Loss_J'].min(),
            'max': df['Net_Energy_Loss_J'].max(),
            'cumulative': df['Cumulative_Energy_Loss_J'].iloc[-1]
        },
        'outflow_volume': {
            'current': df['Outflow_Volume_m3s'].iloc[-1],
            'mean': df['Outflow_Volume_m3s'].mean(),
            'std': df['Outflow_Volume_m3s'].std(),
            'min': df['Outflow_Volume_m3s'].min(),
            'max': df['Outflow_Volume_m3s'].max()
        }
    }
    
    # PDF erstellen
    with PdfPages(output_filename) as pdf:
        
        # === SEITE 1: TITELSEITE UND ÜBERSICHT ===
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('OpenFOAM Live Monitor Report', fontsize=24, fontweight='bold', y=0.95)
        
        # Report-Informationen
        report_info = f"""
        Generiert am: {datetime.now().strftime('%d.%m.%Y um %H:%M:%S')}
        Datei: {os.path.basename(data_file_path)}
        Zeitbereich: {stats['time_range'][0]:.3f} - {stats['time_range'][1]:.3f}
        Datenpunkte: {stats['total_data_points']}
        Aktuelle Zellanzahl: {stats['cell_count']:,}
        """
        
        fig.text(0.1, 0.8, report_info, fontsize=12, verticalalignment='top', 
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.7))
        
        # Aktuelle Werte Tabelle
        current_values_text = f"""
        AKTUELLE WERTE (Letzter Timestep: {df['Timestep'].iloc[-1]:.3f})
        
        Mass Imbalance:      {stats['mass_imbalance']['current']:>8.4f} %
        Volume Diff:         {stats['volume_diff']['current']:>8.4f} %
        Net Power Loss:      {stats['power_loss']['current']:>8.2f} W
        Net Energy Loss:     {stats['energy_loss']['current']:>8.4f} J
        Cumulative Energy:   {stats['energy_loss']['cumulative']:>8.2f} J
        Outflow Volume:      {stats['outflow_volume']['current']:>8.6f} m³/s
        """
        
        fig.text(0.1, 0.5, current_values_text, fontsize=11, verticalalignment='top', 
                fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgreen", alpha=0.7))
        
        # Statistiken Tabelle
        stats_text = f"""
        STATISTISCHE ÜBERSICHT
        
        Mass Imbalance (%)     | Mittel: {stats['mass_imbalance']['mean']:>7.4f} | Std: {stats['mass_imbalance']['std']:>7.4f}
                              | Min:    {stats['mass_imbalance']['min']:>7.4f} | Max: {stats['mass_imbalance']['max']:>7.4f}
        
        Volume Diff (%)        | Mittel: {stats['volume_diff']['mean']:>7.4f} | Std: {stats['volume_diff']['std']:>7.4f}
                              | Min:    {stats['volume_diff']['min']:>7.4f} | Max: {stats['volume_diff']['max']:>7.4f}
        
        Net Power Loss (W)     | Mittel: {stats['power_loss']['mean']:>7.2f} | Std: {stats['power_loss']['std']:>7.2f}
                              | Min:    {stats['power_loss']['min']:>7.2f} | Max: {stats['power_loss']['max']:>7.2f}
        """
        
        fig.text(0.1, 0.2, stats_text, fontsize=10, verticalalignment='top', 
                fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.7))
        
        plt.axis('off')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # === SEITE 2: MASS IMBALANCE UND VOLUME DIFF ===
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8.5))
        fig.suptitle('Mass Imbalance und Volume Diff', fontsize=16, fontweight='bold')
        
        # Mass Imbalance Plot
        ax1.plot(df['Timestep'], df['Mass_Imbalance_Percent'], 'b-', linewidth=1.5, label='Mass Imbalance')
        ax1.scatter(df['Timestep'].iloc[-1], df['Mass_Imbalance_Percent'].iloc[-1], 
                   color='red', s=50, zorder=5, label='Aktueller Wert')
        ax1.axhline(y=stats['mass_imbalance']['mean'], color='orange', linestyle='--', alpha=0.7, label='Mittelwert')
        ax1.set_xlabel('Timestep')
        ax1.set_ylabel('Mass Imbalance (%)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_title(f'Aktuell: {stats["mass_imbalance"]["current"]:.4f}% | Mittel: {stats["mass_imbalance"]["mean"]:.4f}%')
        
        # Volume Diff Plot
        ax2.plot(df['Timestep'], df['Volume_Diff_Percent'], 'g-', linewidth=1.5, label='Volume Diff')
        ax2.scatter(df['Timestep'].iloc[-1], df['Volume_Diff_Percent'].iloc[-1], 
                   color='red', s=50, zorder=5, label='Aktueller Wert')
        ax2.axhline(y=stats['volume_diff']['mean'], color='orange', linestyle='--', alpha=0.7, label='Mittelwert')
        ax2.set_xlabel('Timestep')
        ax2.set_ylabel('Volume Diff (%)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.set_title(f'Aktuell: {stats["volume_diff"]["current"]:.4f}% | Mittel: {stats["volume_diff"]["mean"]:.4f}%')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # === SEITE 3: ENERGY UND POWER PLOTS ===
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8.5))
        fig.suptitle('Energy und Power Loss', fontsize=16, fontweight='bold')
        
        # Net Power Loss Plot
        ax1.plot(df['Timestep'], df['Net_Power_Loss_W'], 'orange', linewidth=1.5, label='Net Power Loss')
        ax1.scatter(df['Timestep'].iloc[-1], df['Net_Power_Loss_W'].iloc[-1], 
                   color='red', s=50, zorder=5, label='Aktueller Wert')
        ax1.axhline(y=stats['power_loss']['mean'], color='blue', linestyle='--', alpha=0.7, label='Mittelwert')
        ax1.set_xlabel('Timestep')
        ax1.set_ylabel('Net Power Loss (W)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_title(f'Aktuell: {stats["power_loss"]["current"]:.2f}W | Mittel: {stats["power_loss"]["mean"]:.2f}W')
        
        # Cumulative Energy Loss Plot
        ax2.plot(df['Timestep'], df['Cumulative_Energy_Loss_J'], 'darkred', linewidth=1.5, label='Kumulierter Energy Loss')
        ax2.scatter(df['Timestep'].iloc[-1], df['Cumulative_Energy_Loss_J'].iloc[-1], 
                   color='red', s=50, zorder=5, label='Aktueller Wert')
        ax2.set_xlabel('Timestep')
        ax2.set_ylabel('Kumulierter Energy Loss (J)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.set_title(f'Gesamt: {stats["energy_loss"]["cumulative"]:.2f}J')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # === SEITE 4: FLOW VOLUME UND NET ENERGY LOSS ===
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8.5))
        fig.suptitle('Flow Volume und Net Energy Loss', fontsize=16, fontweight='bold')
        
        # Outflow Volume Plot
        ax1.plot(df['Timestep'], df['Outflow_Volume_m3s'], 'teal', linewidth=1.5, label='Outflow Volume')
        ax1.scatter(df['Timestep'].iloc[-1], df['Outflow_Volume_m3s'].iloc[-1], 
                   color='red', s=50, zorder=5, label='Aktueller Wert')
        ax1.axhline(y=stats['outflow_volume']['mean'], color='orange', linestyle='--', alpha=0.7, label='Mittelwert')
        ax1.set_xlabel('Timestep')
        ax1.set_ylabel('Outflow Volume (m³/s)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_title(f'Aktuell: {stats["outflow_volume"]["current"]:.6f}m³/s | Mittel: {stats["outflow_volume"]["mean"]:.6f}m³/s')
        
        # Net Energy Loss (pro Timestep) Plot
        ax2.plot(df['Timestep'], df['Net_Energy_Loss_J'], 'purple', linewidth=1.5, label='Net Energy Loss')
        ax2.scatter(df['Timestep'].iloc[-1], df['Net_Energy_Loss_J'].iloc[-1], 
                   color='red', s=50, zorder=5, label='Aktueller Wert')
        ax2.axhline(y=stats['energy_loss']['mean'], color='orange', linestyle='--', alpha=0.7, label='Mittelwert')
        ax2.set_xlabel('Timestep')
        ax2.set_ylabel('Net Energy Loss (J)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.set_title(f'Aktuell: {stats["energy_loss"]["current"]:.4f}J | Mittel: {stats["energy_loss"]["mean"]:.4f}J')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # === SEITE 5: DATENEXPORT ===
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('Datenexport (Letzte 10 Datenpunkte)', fontsize=16, fontweight='bold')
        
        # Letzte 10 Datenpunkte als Tabelle
        if len(df) >= 10:
            table_data = df.tail(10)
        else:
            table_data = df
            
        # Erstelle Tabellen-Text
        table_text = "Timestep    Cells       Mass(%)     Vol(%)      Power(W)    Energy(J)   Flow(m³/s)\n"
        table_text += "="*90 + "\n"
        
        for _, row in table_data.iterrows():
            table_text += f"{row['Timestep']:8.3f}    {row['Cell_Count']:7d}     "
            table_text += f"{row['Mass_Imbalance_Percent']:7.4f}     {row['Volume_Diff_Percent']:6.4f}     "
            table_text += f"{row['Net_Power_Loss_W']:7.2f}     {row['Net_Energy_Loss_J']:8.4f}   "
            table_text += f"{row['Outflow_Volume_m3s']:9.6f}\n"
        
        fig.text(0.05, 0.9, table_text, fontsize=8, verticalalignment='top', 
                fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.7))
        
        # CSV-Export Hinweis
        csv_filename = output_filename.replace('.pdf', '_data.csv')
        df.to_csv(csv_filename, index=False)
        
        export_text = f"""
        DATENEXPORT
        
        📊 Vollständige Daten wurden exportiert nach:
        {csv_filename}
        
        📄 Dieser PDF-Report:
        {output_filename}
        
        Insgesamt {len(df)} Datenpunkte exportiert.
        """
        
        fig.text(0.05, 0.4, export_text, fontsize=12, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.7))
        
        plt.axis('off')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    print(f"✅ PDF-Report erstellt: {output_filename}")
    print(f"📊 CSV-Daten exportiert: {csv_filename}")
    print(f"📈 {len(df)} Datenpunkte verarbeitet")
    
    return output_filename

# Monitor-Instanz erstellen
monitor = LiveMassImbalanceMonitor(data_file_path, update_interval=REFRESH_INTERVAL)

print("\n" + "="*60)
print("MASS IMBALANCE MONITOR")
print("="*60)
print("Verfügbare Befehle:")
print("1. monitor.update_plot()           - Einmaliges Update")
print("2. monitor.start_auto_monitoring() - Automatisches Monitoring starten")
print("3. monitor.stop_monitoring()       - Monitoring stoppen")
print("4. monitor.create_pdf_snapshot()   - PDF-Report der aktuellen Monitor-Ansicht")
print("5. create_pdf_report()             - PDF-Report erstellen (alternative Funktion)")
print("="*60)

# Automatisches Monitoring-Script
def start_continuous_monitoring(plot_mode="console"):
    """
    Startet kontinuierliches Monitoring mit verschiedenen Anzeigemodi
    plot_mode: "console", "browser"
    """
    data_file_path = "/Users/philipp.simlinger/openFOAM/work/validation/V03/postProcess/EnergyLoss/Data"
    
    monitor = LiveMassImbalanceMonitor(data_file_path, update_interval=REFRESH_INTERVAL)
    
    if plot_mode == "console":
        monitor.start_monitoring(mode='console')
    elif plot_mode == "browser":
        monitor.start_monitoring(mode='browser')
    else:
        print(f"Unbekannter Modus: {plot_mode}")
        print("Verfügbare Modi: 'console', 'browser'")

# Einfacher Start-Befehl
def auto_start():
    """Startet automatisches Monitoring mit Auswahlmöglichkeiten"""
    print("\n" + "="*60)
    print("LIVE MONITORING OPTIONEN")
    print("="*60)
    print("1. Nur Konsole (empfohlen) - Keine Plots, nur Zahlen")
    print("2. Browser Dashboard - Live-Updates im Browser")
    print("3. Nein - Kein automatisches Monitoring")
    print("="*60)
    
    try:
        choice = input("Wählen Sie eine Option (1-3): ").strip()
        
        if choice == "1":
            start_continuous_monitoring("console")
        elif choice == "2":
            start_continuous_monitoring("browser")
        elif choice == "3":
            print("Kein automatisches Monitoring gestartet")
            print("Verwenden Sie start_continuous_monitoring('console') um später zu starten")
        else:
            print("Ungültige Auswahl. Verwenden Sie:")
            print("start_continuous_monitoring('console')  # Nur Konsole")
            print("start_continuous_monitoring('browser')  # Browser Dashboard")
            
    except KeyboardInterrupt:
        print("\nAbgebrochen. Verwenden Sie start_continuous_monitoring() um zu starten")

# Initialer Aufruf
auto_start()


