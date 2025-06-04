# -*- coding: utf-8 -*-
"""
PC Fleet Summary Pie Chart Report
--------------------------------
This script reads a machine data JSON file and generates a summary HTML report.
The report displays pie charts for all major specs (GPU model, RAM size, CPU model, OS version, and storage size),
giving you a fun, visual overview of your entire fleet at a glance!

Place this script in the same folder as your machine_data.json file.
Run it to produce a beautiful summary HTML report for your team!
"""
import os
import json

def get_summary_data(data):
    """Aggregate counts and machine names for GPU model, RAM size, CPU model, OS version, and storage size across all machines."""
    gpu = {}
    ram = {}
    cpu = {}
    osv = {}
    storage = {}
    for machine_name, machine in data.items():
        # GPU models
        for gpu_item in machine.get('gpu', []):
            name = gpu_item.get('name', 'Unknown')
            if name:
                if name not in gpu:
                    gpu[name] = {'count': 0, 'machines': []}
                gpu[name]['count'] += 1
                gpu[name]['machines'].append(machine_name)
        # RAM sizes
        ram_total = machine.get('ram', {}).get('total', 'Unknown')
        if ram_total:
            if ram_total not in ram:
                ram[ram_total] = {'count': 0, 'machines': []}
            ram[ram_total]['count'] += 1
            ram[ram_total]['machines'].append(machine_name)
        # CPU models
        cpu_model = machine.get('cpu', {}).get('model', 'Unknown')
        if cpu_model:
            if cpu_model not in cpu:
                cpu[cpu_model] = {'count': 0, 'machines': []}
            cpu[cpu_model]['count'] += 1
            cpu[cpu_model]['machines'].append(machine_name)
        # OS version
        os_version = machine.get('os', 'Unknown')
        if os_version:
            if os_version not in osv:
                osv[os_version] = {'count': 0, 'machines': []}
            osv[os_version]['count'] += 1
            osv[os_version]['machines'].append(machine_name)
        # Storage size (sum all drives per machine, rounded to nearest 10GB)
        total_storage = 0
        for s in machine.get('storage', []):
            try:
                total_storage += float(s.get('total', 0).split()[0])
            except Exception:
                continue
        if total_storage > 0:
            label = f"{round(total_storage/10)*10} GB"
            if label not in storage:
                storage[label] = {'count': 0, 'machines': []}
            storage[label]['count'] += 1
            storage[label]['machines'].append(machine_name)
    return {
        'gpu': gpu,
        'ram': ram,
        'cpu': cpu,
        'os': osv,
        'storage': storage
    }

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>How is everyone's PC doing at Ennead?</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f9; margin: 0; padding: 0; }
        .container { max-width: 1200px; margin: 40px auto; background: #fff; border-radius: 10px; box-shadow: 0 2px 8px #ccc; padding: 32px; }
        h1 { text-align: center; color: #2d3e50; }
        .summary-charts { display: flex; flex-wrap: wrap; justify-content: center; gap: 40px; margin-bottom: 32px; }
        .chart-container { width: 350px; height: 350px; margin: 0 auto 24px auto; }
        .note { color: #888; font-size: 0.95em; text-align: center; }
        .machine-select-container { text-align: center; margin-top: 40px; }
        .machine-details { max-width: 800px; margin: 24px auto; }
        .spec-table { width: 100%; border-collapse: collapse; margin-top: 16px; }
        .spec-table th, .spec-table td { border: 1px solid #e0e0e0; padding: 8px 12px; text-align: left; }
        .spec-table th { background: #eaf6fb; color: #2d3e50; }
        .section-title { margin-top: 24px; color: #1a7fa4; }
    </style>
</head>
<body>
    <div class="container">
        <h1>How is everyone's PC doing at Ennead?</h1>
        <div class="summary-charts">
            <div class="chart-container"><canvas id="gpu-summary"></canvas></div>
            <div class="chart-container"><canvas id="ram-summary"></canvas></div>
            <div class="chart-container"><canvas id="cpu-summary"></canvas></div>
            <div class="chart-container"><canvas id="os-summary"></canvas></div>
            <div class="chart-container"><canvas id="storage-summary"></canvas></div>
        </div>
        <div class="machine-select-container">
            <label for="machine-select"><b>Show details for:</b></label>
            <select id="machine-select">
                <option value="">-- Select a machine --</option>
            </select>
        </div>
        <div class="machine-details" id="machine-details"></div>
        <p class="note">Made with ❤️ by EnneadTab</p>
    </div>
    <script>
        const summary = __SUMMARY__;
        const data = __DATA__;
        function renderPieChart(ctx, summaryObj, title) {
            const labels = Object.keys(summaryObj);
            const values = labels.map(l => summaryObj[l].count);
            const machineLists = labels.map(l => summaryObj[l].machines);
            const colors = [
                '#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF', '#B2FF66', '#FF66B2', '#66FFB2',
                '#A266FF', '#FFB266', '#66B2FF', '#B266FF', '#FF66A2', '#B2FF66', '#66FFB2', '#FF6666', '#66FF66', '#6666FF'
            ];
            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: values,
                        backgroundColor: colors.slice(0, labels.length),
                    }]
                },
                options: {
                    responsive: false,
                    plugins: {
                        legend: { position: 'bottom' },
                        title: { display: true, text: title },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.label;
                                },
                                afterLabel: function(context) {
                                    const idx = context.dataIndex;
                                    const count = values[idx];
                                    const machines = machineLists[idx];
                                    let lines = [`${count} machine(s):`];
                                    lines = lines.concat(machines.map(n => '  ' + n));
                                    return lines;
                                }
                            }
                        }
                    }
                }
            });
        }
        renderPieChart(
            document.getElementById('gpu-summary'),
            summary.gpu,
            'GPU Model Distribution'
        );
        renderPieChart(
            document.getElementById('ram-summary'),
            summary.ram,
            'RAM Size Distribution'
        );
        renderPieChart(
            document.getElementById('cpu-summary'),
            summary.cpu,
            'CPU Model Distribution'
        );
        renderPieChart(
            document.getElementById('os-summary'),
            summary.os,
            'OS Version Distribution'
        );
        renderPieChart(
            document.getElementById('storage-summary'),
            summary.storage,
            'Total Storage (per machine)'
        );
        // Populate machine select
        const select = document.getElementById('machine-select');
        const machineNames = Object.keys(data);
        machineNames.forEach((name, idx) => {
            const opt = document.createElement('option');
            opt.value = name;
            opt.textContent = name;
            select.appendChild(opt);
        });
        // Show first machine by default
        if (machineNames.length > 0) {
            select.value = machineNames[0];
            showMachineDetails(machineNames[0]);
        }
        select.addEventListener('change', function() {
            showMachineDetails(this.value);
        });
        function showMachineDetails(name) {
            const detailsDiv = document.getElementById('machine-details');
            if (!name || !data[name]) {
                detailsDiv.innerHTML = '';
                return;
            }
            const machine = data[name];
            let html = '';
            html += `<h2 class='section-title'>${name} Details</h2>`;
            html += `<table class='spec-table'>`;
            for (const section of ['cpu','gpu','ram','storage','os','user','python','network','system_age_days','last_updated']) {
                if (!machine[section]) continue;
                if (Array.isArray(machine[section])) {
                    machine[section].forEach((item, idx) => {
                        html += `<tr><th>${section} #${idx+1}</th><td>`;
                        if (typeof item === 'object') {
                            html += '<table class="spec-table">';
                            for (const [k, v] of Object.entries(item)) html += `<tr><th>${k}</th><td>${v}</td></tr>`;
                            html += '</table>';
                        } else {
                            html += item;
                        }
                        html += `</td></tr>`;
                    });
                } else if (typeof machine[section] === 'object') {
                    html += `<tr><th>${section}</th><td><table class="spec-table">`;
                    for (const [k, v] of Object.entries(machine[section])) html += `<tr><th>${k}</th><td>${v}</td></tr>`;
                    html += '</table></td></tr>';
                } else {
                    html += `<tr><th>${section}</th><td>${machine[section]}</td></tr>`;
                }
            }
            html += `</table>`;
            detailsDiv.innerHTML = html;
        }
    </script>
</body>
</html>
"""

def main():
    """Reads machine_data.json and generates a summary HTML report in the same folder."""
    folder = "L:\\4b_Applied Computing\\EnneadTab-DB\\Shared Data Dump\\_internal reports"
    json_path = os.path.join(folder, 'machine_data.json')
    html_path = os.path.join(folder, 'machine_report.html')
    if not os.path.exists(json_path):
        return
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    summary = get_summary_data(data)
    html = HTML_TEMPLATE.replace('__SUMMARY__', json.dumps(summary)).replace('__DATA__', json.dumps(data))
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    main()