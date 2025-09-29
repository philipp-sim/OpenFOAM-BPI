#!/usr/bin/env python3
"""
Einfache PDF-Report Erstellung für OpenFOAM Live Monitor
"""

import pandas as pd
import matplotlib.pyplot as plt
import re
import numpy as np
import os
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

def parse_openfoam_data(file_path):
    """OpenFOAM Data Parser"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        timestep_pattern = r'Timestep\s+([\d\.]+)\s+\|'
        cell_count_pattern = r'Cells\s+(\d+)'
        mass_imbalance_pattern = r'Mass imbalance:.*?\(([-\d\.]+)\s*%\)'
        volume_diff_pattern = r'Volume diff:.*?\(([-\d\.]+)\s*%\)'
        net_power_loss_pattern = r'Net power loss:\s+([-\d\.]+)\s+W'
        net_energy_loss_pattern = r'Net energy loss:\s+([-\d\.]+)\s+J'
        outflow_volume_pattern = r'Outflow volume:\s+([-\d\.]+)\s+m³/s'
        
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
                ts_match = re.search(timestep_pattern, block)
                if not ts_match:
                    continue
                timestep = float(ts_match.group(1))
                
                cc_match = re.search(cell_count_pattern, block)
                cell_count = int(cc_match.group(1)) if cc_match else 0
                
                mi_match = re.search(mass_imbalance_pattern, block)
                mass_imbalance = float(mi_match.group(1)) if mi_match else 0.0
                
                vd_match = re.search(volume_diff_pattern, block)
                volume_diff = float(vd_match.group(1)) if vd_match else 0.0
                
                npl_match = re.search(net_power_loss_pattern, block)
                net_power_loss = float(npl_match.group(1)) if npl_match else 0.0
                
                nel_match = re.search(net_energy_loss_pattern, block)
                net_energy_loss = float(nel_match.group(1)) if nel_match else 0.0
                
                ofv_match = re.search(outflow_volume_pattern, block)
                outflow_volume = float(ofv_match.group(1)) if ofv_match else 0.0
                
                timesteps.append(timestep)
                cell_counts.append(cell_count)
                mass_imbalances.append(mass_imbalance)
                volume_diffs.append(volume_diff)
                net_power_losses.append(net_power_loss)
                net_energy_losses.append(net_energy_loss)
                outflow_volumes.append(outflow_volume)
                
            except (ValueError, AttributeError):
                continue
        
        return timesteps, cell_counts, mass_imbalances, volume_diffs, net_power_losses, net_energy_losses, outflow_volumes
        
    except FileNotFoundError:
        print(f' Datei {file_path} nicht gefunden!')
        return [], [], [], [], [], [], []
    except Exception as e:
        print(f' Fehler beim Parsen der Datei: {e}')
        return [], [], [], [], [], [], []

def create_pdf_report(data_file_path=None, output_filename=None):
    """Erstellt einen umfassenden PDF-Report"""
    
    if data_file_path is None:
        data_file_path = "/Users/philipp.simlinger/openFOAM/work/validation/V03/postProcess/EnergyLoss/Data"
    
    # Report-Verzeichnis erstellen falls es nicht existiert
    report_dir = "report"
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
        print(f" Report-Verzeichnis erstellt: {report_dir}")
    
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"OpenFOAM_Monitor_Report_{timestamp}.pdf"
    
    # PDF-Datei in report-Ordner speichern
    output_filename = os.path.join(report_dir, output_filename)
    
    print(f" Erstelle PDF-Report: {output_filename}")
    
    # Daten laden
    timesteps, cell_counts, mass_imbalances, volume_diffs, net_power_losses, net_energy_losses, outflow_volumes = parse_openfoam_data(data_file_path)
    
    if not timesteps:
        print(" Keine Daten gefunden. PDF kann nicht erstellt werden.")
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
        report_info = f"""Generiert am: {datetime.now().strftime('%d.%m.%Y um %H:%M:%S')}
Datei: {os.path.basename(data_file_path)}
Zeitbereich: {stats['time_range'][0]:.3f} - {stats['time_range'][1]:.3f}
Datenpunkte: {stats['total_data_points']}
Aktuelle Zellanzahl: {stats['cell_count']:,}"""
        
        fig.text(0.1, 0.8, report_info, fontsize=12, verticalalignment='top', 
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.7))
        
        # Aktuelle Werte
        current_values_text = f"""AKTUELLE WERTE (Letzter Timestep: {df['Timestep'].iloc[-1]:.3f})

Mass Imbalance:      {stats['mass_imbalance']['current']:>8.4f} %
Volume Diff:         {stats['volume_diff']['current']:>8.4f} %
Net Power Loss:      {stats['power_loss']['current']:>8.2f} W
Net Energy Loss:     {stats['energy_loss']['current']:>8.4f} J
Cumulative Energy:   {stats['energy_loss']['cumulative']:>8.2f} J
Outflow Volume:      {stats['outflow_volume']['current']:>8.6f} m³/s"""
        
        fig.text(0.1, 0.5, current_values_text, fontsize=11, verticalalignment='top', 
                fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgreen", alpha=0.7))
        
        # Statistiken
        stats_text = f"""STATISTISCHE ÜBERSICHT

Mass Imbalance (%)     | Mittel: {stats['mass_imbalance']['mean']:>7.4f} | Std: {stats['mass_imbalance']['std']:>7.4f}
                      | Min:    {stats['mass_imbalance']['min']:>7.4f} | Max: {stats['mass_imbalance']['max']:>7.4f}

Volume Diff (%)        | Mittel: {stats['volume_diff']['mean']:>7.4f} | Std: {stats['volume_diff']['std']:>7.4f}
                      | Min:    {stats['volume_diff']['min']:>7.4f} | Max: {stats['volume_diff']['max']:>7.4f}

Net Power Loss (W)     | Mittel: {stats['power_loss']['mean']:>7.2f} | Std: {stats['power_loss']['std']:>7.2f}
                      | Min:    {stats['power_loss']['min']:>7.2f} | Max: {stats['power_loss']['max']:>7.2f}"""
        
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
    
    # CSV-Export auch in report-Ordner
    csv_filename = output_filename.replace('.pdf', '_data.csv')
    df.to_csv(csv_filename, index=False)
    
    print(f" PDF-Report erstellt: {output_filename}")
    print(f" CSV-Daten exportiert: {csv_filename}")
    print(f" {len(df)} Datenpunkte verarbeitet")
    #print(f" Aktuelle Mass Imbalance: {stats['mass_imbalance']['current']:.4f}%")
    
    return output_filename

if __name__ == "__main__":
    # PDF Report erstellen
    create_pdf_report()