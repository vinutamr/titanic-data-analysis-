<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Titanic Data Analysis (HTML)</title>
  <script src="https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js"></script>
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
  <style>
    body{font-family: Inter, system-ui, -apple-system, Arial; padding:22px; background:#0f172a; color:#e6eef8}
    .card{background:#0b1220; border-radius:12px; padding:16px; box-shadow:0 6px 18px rgba(2,6,23,0.6); margin-bottom:18px}
    h1{font-size:22px; margin-bottom:6px}
    label.button{display:inline-block;background:#06b6d4;color:#021024;padding:8px 12px;border-radius:8px;cursor:pointer}
    table{width:100%; border-collapse:collapse;margin-top:8px}
    th,td{padding:6px 8px;border-bottom:1px solid rgba(255,255,255,0.04); text-align:left}
    .flex{display:flex;gap:12px}
    .half{flex:1}
    pre{white-space:pre-wrap;background:#061226;padding:10px;border-radius:8px}
    .muted{color:#9aa9bf}
    .small{font-size:13px}
  </style>
</head>
<body>
  <div class="card">
    <h1>Titanic Data Analysis — HTML version</h1>
    <p class="muted small">Upload your <code>titanic.csv</code> (same columns as the classic dataset) and the page will compute stats & show plots in your browser.</p>
    <input id="fileInput" type="file" accept=".csv" />
    <button id="sampleBtn">Load sample (if available)</button>
  </div>

  <div id="summary" class="card" style="display:none">
    <h2>Basic exploration</h2>
    <div id="basicInfo"></div>
  </div>

  <div id="tables" class="card" style="display:none">
    <h2>Data preview</h2>
    <div id="firstRows"></div>
    <h3>First 5 (Name & Age)</h3>
    <div id="firstNames"></div>
  </div>

  <div id="analysis" class="card" style="display:none">
    <h2>Analysis</h2>
    <div id="analysisText"></div>
  </div>

  <div id="plots" style="display:none">
    <div class="card">
      <h3>Survival Count</h3>
      <div id="plot_survived" style="height:320px"></div>
    </div>
    <div class="card flex">
      <div class="half">
        <h3>Survival Rate by Class</h3>
        <div id="plot_pclass" style="height:300px"></div>
      </div>
      <div class="half">
        <h3>Survival Rate by Gender</h3>
        <div id="plot_sex" style="height:300px"></div>
      </div>
    </div>
    <div class="card">
      <h3>Age Distribution</h3>
      <div id="plot_age" style="height:360px"></div>
    </div>
  </div>

  <script>
    const fileInput = document.getElementById('fileInput');
    const sampleBtn = document.getElementById('sampleBtn');

    fileInput.addEventListener('change', (e)=>{
      const f = e.target.files[0];
      if(!f) return;
      Papa.parse(f, {header:true, dynamicTyping:true, skipEmptyLines:true, complete: (results)=>{
        const data = results.data;
        analyze(data);
      }});
    });

    // If you want, you can drop in a small built-in sample later. For now sampleBtn does nothing.
    sampleBtn.addEventListener('click', ()=>{alert('Upload your local titanic.csv using the file chooser.');});

    function analyze(rows){
      // Normalize column names to trimmed strings
      if(!rows || rows.length===0){alert('No rows parsed.'); return}

      // Convert keys to trimmed versions for safety
      rows = rows.map(r=>{
        const nr = {};
        for(const k in r) nr[k.trim()] = r[k];
        return nr;
      });

      // If Age missing, fill with mean
      const ageValues = rows.map(r=>isFinite(r['Age'])?r['Age']:null).filter(v=>v!==null);
      const ageMean = ageValues.reduce((a,b)=>a+b,0)/Math.max(1,ageValues.length);
      rows.forEach(r=>{ if(!isFinite(r['Age'])) r['Age'] = +ageMean.toFixed(2); });

      // Drop Cabin and Ticket fields when displaying (they may still exist in objects)

      // Basic exploration
      const first10 = rows.slice(0,10);
      const columns = Array.from(new Set(Object.keys(rows[0])));
      const shape = [rows.length, columns.length];

      const fareVals = rows.map(r=>isFinite(r['Fare'])?r['Fare']:null).filter(v=>v!==null);
      const maxFare = fareVals.length?Math.max(...fareVals):'N/A';

      // First 5 Name & Age
      const first5 = rows.slice(0,5).map(r=>({Name:r['Name']||'N/A', Age:r['Age']}));

      // Survival stats
      const survivedVals = rows.map(r=> (r['Survived']===1 || r['Survived']=='1' || r['Survived']===true) ? 1 : 0 );
      const overallSurvRate = (survivedVals.reduce((a,b)=>a+b,0)/survivedVals.length) || 0;

      // Survival by Sex
      const bySex = {};
      rows.forEach((r,i)=>{
        const sex = (r['Sex']||'unknown').toString();
        const s = survivedVals[i];
        if(!bySex[sex]) bySex[sex] = {sum:0,count:0};
        bySex[sex].sum += s; bySex[sex].count += 1;
      });
      const sexRates = Object.entries(bySex).map(([k,v])=>({sex:k, rate: v.count? v.sum/v.count:0, count:v.count}));

      // Survival by Pclass
      const byClass = {};
      rows.forEach((r,i)=>{
        const p = r['Pclass']!==undefined? r['Pclass'] : (r['Pclass']||'unknown');
        const key = p===null ? 'unknown' : String(p);
        const s = survivedVals[i];
        if(!byClass[key]) byClass[key] = {sum:0,count:0};
        byClass[key].sum += s; byClass[key].count += 1;
      });
      const classRates = Object.entries(byClass).map(([k,v])=>({pclass:k, rate: v.count? v.sum/v.count:0, count:v.count})).sort((a,b)=>a.pclass-b.pclass);

      // Average age by survival status
      const ageBySurv = {0:[], 1:[]};
      rows.forEach((r,i)=>{ const s = survivedVals[i]; if(s===1) ageBySurv[1].push(r['Age']); else ageBySurv[0].push(r['Age']); });
      const avgAgeSurv = {0: mean(ageBySurv[0]), 1: mean(ageBySurv[1])};

      // Render summary
      document.getElementById('summary').style.display='block';
      document.getElementById('tables').style.display='block';
      document.getElementById('analysis').style.display='block';
      document.getElementById('plots').style.display='block';

      document.getElementById('basicInfo').innerHTML = `
        <table>
          <tr><th>Columns</th><td>${columns.join(', ')}</td></tr>
          <tr><th>Shape (rows,cols)</th><td>${shape.join(', ')}</td></tr>
          <tr><th>Average Age</th><td>${ageMean.toFixed(2)}</td></tr>
          <tr><th>Maximum Fare</th><td>${maxFare}</td></tr>
        </table>
      `;

      // First rows table
      document.getElementById('firstRows').innerHTML = renderTable(first10, ['Name','Pclass','Sex','Age','Fare','Survived']);
      document.getElementById('firstNames').innerHTML = renderTable(first5, ['Name','Age']);

      // Analysis text
      const analysisDiv = document.getElementById('analysisText');
      analysisDiv.innerHTML = `
        <p><strong>Overall survival rate:</strong> ${(overallSurvRate*100).toFixed(2)}%</p>
        <p><strong>Survival rate by gender:</strong></p>
        ${renderKeyValueTable(sexRates.map(s=>[s.sex, (s.rate*100).toFixed(2)+"% (n="+s.count+")"]))}
        <p><strong>Survival rate by passenger class:</strong></p>
        ${renderKeyValueTable(classRates.map(c=>[c.pclass, (c.rate*100).toFixed(2)+"% (n="+c.count+")"]))}
        <p><strong>Average age by survival status:</strong></p>
        ${renderKeyValueTable([['Survived=0', avgAgeSurv[0]!==null?avgAgeSurv[0].toFixed(2):'N/A'], ['Survived=1', avgAgeSurv[1]!==null?avgAgeSurv[1].toFixed(2):'N/A']])}
      `;

      // Plots
      plotSurvivedCounts(survivedVals);
      plotPclassRates(classRates);
      plotSexRates(sexRates);
      plotAgeHistogram(rows.map(r=>r['Age']));
    }

    // Helpers
    function mean(arr){ if(!arr||arr.length===0) return null; return arr.reduce((a,b)=>a+b,0)/arr.length; }

    function renderTable(rows, cols){
      cols = cols || Object.keys(rows[0] || {});
      let html = '<div style="overflow:auto"><table><thead><tr>' + cols.map(c=><th>${c}</th>).join('') + '</tr></thead><tbody>';
      rows.forEach(r=>{ html += '<tr>' + cols.map(c=><td>${escapeHTML(r[c]===undefined?'':r[c])}</td>).join('') + '</tr>'; });
      html += '</tbody></table></div>';
      return html;
    }

    function renderKeyValueTable(pairs){
      let html = '<table>';
      pairs.forEach(([k,v])=>{ html += <tr><th style="width:190px">${escapeHTML(k)}</th><td>${escapeHTML(v)}</td></tr>; });
      html += '</table>';
      return html;
    }

    function escapeHTML(s){ if(s===null||s===undefined) return ''; return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

    // Plot helpers using Plotly
    function plotSurvivedCounts(survivedArr){
      const counts = survivedArr.reduce((acc,v)=>{ acc[v] = (acc[v]||0)+1; return acc; },{});
      const x = Object.keys(counts).map(k=>k);
      const y = x.map(k=>counts[k]);
      const trace = { x: x, y: y, type: 'bar', marker:{opacity:0.9} };
      const layout = {margin:{t:30,l:40,r:20,b:40}, xaxis:{title:'Survived (0=No,1=Yes)'}, yaxis:{title:'Count'}};
      Plotly.newPlot('plot_survived',[trace],layout,{displayModeBar:false});
    }

    function plotPclassRates(classRates){
      const x = classRates.map(c=>c.pclass);
      const y = classRates.map(c=>c.rate);
      const trace = { x: x, y: y, type: 'bar' };
      const layout = {margin:{t:30,l:40,r:20,b:40}, xaxis:{title:'Pclass'}, yaxis:{title:'Survival Rate', tickformat:'.0%'}};
      Plotly.newPlot('plot_pclass',[trace],layout,{displayModeBar:false});
    }

    function plotSexRates(sexRates){
      const x = sexRates.map(s=>s.sex);
      const y = sexRates.map(s=>s.rate);
      const trace = { x: x, y: y, type: 'bar' };
      const layout = {margin:{t:30,l:40,r:20,b:40}, xaxis:{title:'Sex'}, yaxis:{title:'Survival Rate', tickformat:'.0%'}};
      Plotly.newPlot('plot_sex',[trace],layout,{displayModeBar:false});
    }

    function plotAgeHistogram(ageArr){
      const trace = { x: ageArr, type:'histogram', nbinsx:20 };
      const layout = {margin:{t:30,l:40,r:20,b:40}, xaxis:{title:'Age'}, yaxis:{title:'Count'}};
      Plotly.newPlot('plot_age',[trace],layout,{displayModeBar:false});
    }

  </script>
</body>
</html>
