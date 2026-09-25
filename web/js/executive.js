/* Presentation derived only from the published dashboard contract. */
function kpiSparkline(values,label){
 const finite=values.filter(Number.isFinite),min=Math.min(...finite),max=Math.max(...finite);
 const point=(v,i)=>`${(4+i*152/Math.max(1,values.length-1)).toFixed(1)},${(34-(v-min)/(max-min||1)*28).toFixed(1)}`;
 if(finite.length<2)return `<svg class="kpi-sparkline snapshot" viewBox="0 0 160 40" role="img" aria-label="${h(label)}: one snapshot; historical trend unavailable"><path d="M4 32H156"/><circle cx="80" cy="20" r="3"/></svg>`;
 let path='',connected=false;values.forEach((v,i)=>{if(!Number.isFinite(v)){connected=false;return}path+=`${connected?'L':'M'}${point(v,i)} `;connected=true});
 return `<svg class="kpi-sparkline" viewBox="0 0 160 40" role="img" aria-label="${h(label)}"><path d="${path}"/></svg>`;
}
function polishKpis(data,rows,from,to,region){
 const all=(data.sales_trend_by_region||[]).filter(r=>region==='all'||r.Region===region),monthly=new Map();
 all.forEach(r=>monthly.set(r.YearMonth,(monthly.get(r.YearMonth)||0)+Number(r.Revenue||0)));
 const yoy=rows.map(r=>{const prior=monthly.get(`${Number(r.YearMonth.slice(0,4))-1}${r.YearMonth.slice(4)}`);return prior?(r.Revenue/prior-1)*100:null});
 const specs={revenue:[rows.map(r=>r.Revenue),'Monthly invoiced revenue'],profit:[rows.map(r=>r.GrossProfit),'Monthly gross profit'],orders:[rows.map(r=>r.Orders),'Monthly orders'],'gm-kpi':[rows.map(r=>r.Revenue?r.GrossProfit/r.Revenue*100:null),'Monthly gross margin'],'yoy':[yoy,'Monthly revenue YoY change'],'customers-kpi':[[data.executive_kpis.customers],'Customer snapshot'],'inventory-kpi':[[data.executive_kpis.inventory_value],'Inventory snapshot'],'po-value':[[data.executive_kpis.open_po_value],'Purchase commitment snapshot']};
 for(const [id,[values,label]] of Object.entries(specs)){
  const card=document.getElementById(id).closest('.kpi');card.querySelector('.sparkline-wrap')?.remove();
  const snapshot=['customers-kpi','inventory-kpi','po-value'].includes(id);
  card.insertAdjacentHTML('beforeend',`<div class="sparkline-wrap">${kpiSparkline(values,label)}<span>${snapshot?'Snapshot · history unavailable':id==='yoy'?'Monthly YoY · selected range':'Monthly trend · selected range'}</span></div>`);
  if(snapshot)card.querySelector('.kpi-context').innerHTML='<span class="trend-badge neutral">— No prior period</span><span>Full dataset</span>';
  card.querySelectorAll('.trend-badge:not(.neutral)').forEach(b=>{b.textContent=`${b.classList.contains('down')?'↓':'↑'} ${b.textContent}`});
 }
 const card=document.querySelector('#yoy').closest('.kpi');let context=card.querySelector('.kpi-context');if(!context){context=document.createElement('div');context.className='kpi-context';card.appendChild(context)}
 const current=Number.parseFloat(document.querySelector('#yoy').textContent),year=Number(to.slice(0,4));
 context.innerHTML=`<span class="trend-badge ${Number.isFinite(current)?current<0?'down':'':'neutral'}">${Number.isFinite(current)?`${current<0?'↓':'↑'} ${current<0?'Decrease':'Increase'}`:'No prior year'}</span><span>${year} vs ${year-1} · months ${from.slice(5)}–${to.slice(5)}</span>`;
}
function renderExecutiveSignals(data){
 const f=data.business_findings||{},k=data.executive_kpis||{},candidates=[];
 const add=(score,title,value,detail,target)=>{if(Number.isFinite(score))candidates.push({score,title,value,detail,target})};
 const exposure=Number(f.dead_inventory_value),stock=Number(f.critical_stockout_sku_warehouse_rows);
 if(exposure>0||stock>0)add(80+Math.min(20,exposure/Math.max(1,k.inventory_value)*20),'Inventory exposure',money(exposure)+' dead inventory',`${integer(stock)} critical SKU / warehouse positions require review.`,'inventory');
 const years=Object.entries(f.vendor_one_average_actual_lead_days_by_year||{}).sort(([a],[b])=>a.localeCompare(b));
 if(years.length>1){const first=years[0],last=years.at(-1),change=last[1]-first[1];add(change>0?75+Math.min(20,change):25,'Supplier lead time',`${change>=0?'+':''}${change.toFixed(1)} days`, `Vendor V0001: ${first[1]} days in ${first[0]} → ${last[1]} in ${last[0]}.`,'purchasing')}
 const count=Number(f.valuable_customers_inactive_over_60_days);
 if(count>0)add(70+Math.min(10,count/10),'Customer retention',`${integer(count)} high-value accounts`,'Each exceeds $25K lifetime revenue and has been inactive for over 60 days.','customers');
 const warehouses=Object.entries(f.warehouse_average_ship_days||{}).filter(([,v])=>Number.isFinite(v)).sort((a,b)=>b[1]-a[1]);
 if(warehouses.length>1){const slow=warehouses[0],fast=warehouses.at(-1);add(55+Math.min(20,(slow[1]-fast[1])*5),'Warehouse service',`${slow[0]} · ${slow[1].toFixed(1)} days`,`${(slow[1]-fast[1]).toFixed(1)} days slower than ${fast[0]} on average order-to-ship time.`,'operations')}
 const trend=data.sales_trend||[],a=trend.at(-2),b=trend.at(-1);
 if(a?.Revenue&&b?.Revenue){const delta=(b.GrossProfit/b.Revenue-a.GrossProfit/a.Revenue)*100;add(delta<0?65+Math.min(25,-delta*10):30,'Margin movement',`${delta>=0?'+':''}${delta.toFixed(2)} pp`,`${b.YearMonth} vs ${a.YearMonth}; latest gross margin ${(b.GrossProfit/b.Revenue*100).toFixed(1)}%.`,'sales')}
 if(k.open_po_value>0)add(60,'Purchasing commitments',money(k.open_po_value),'Outstanding unreceived purchase value across all vendors and warehouses.','purchasing');
 const section=document.createElement('section');section.className='executive-signals';section.id='executive-signals';section.setAttribute('aria-labelledby','signals-title');
 const selected=candidates.sort((a,b)=>b.score-a.score||a.title.localeCompare(b.title)).slice(0,5);
 section.innerHTML=`<div class="metric-heading"><h2 id="signals-title">Executive Signals</h2><span>Full dataset · refreshed with each published run</span></div><div class="signal-list">${selected.map((s,i)=>`<a class="signal-card" href="#${s.target}"><span class="signal-rank">0${i+1}</span><div><small>${h(s.title)}</small><strong>${h(s.value)}</strong><p>${h(s.detail)}</p></div><span aria-hidden="true">↗</span></a>`).join('')||'<p>No observations available in this dataset.</p>'}</div><details class="signal-method"><summary>How signals are prioritized</summary><p>Rule-based triage: inventory exposure first, followed by worsening supplier lead time, inactive high-value customers, service gaps, purchasing commitments, and margin movement. Larger supplier delays, service gaps, or margin declines raise priority. The five highest scores are shown. These are investigation prompts, not forecasts or business targets. Overview filters do not change these full-dataset signals.</p></details>`;
 document.querySelector('.kpi-grid').insertAdjacentElement('afterend',section);
}
function renderLineage(data){
 const stages=[
 ['ERP','Synthetic source systems','Seeded generation creates fictional customers, products, orders, invoices, purchase orders, inventory movements, and returns.','python/generators'],
 ['Raw','Original extracts','CSV extracts preserve the generated source records before cleaning.','data/raw'],
 ['Staging','Standardized records','Python cleaning standardizes the raw files into processed data; SQL staging scripts document the warehouse implementation.','etl/clean_data.py'],
 ['Star Schema','Dimensions & facts','Conformed dimensions and transaction-grain facts define the analytical model. SQL scripts provide the warehouse design; the hosted refresh uses Python and CSV processing.','sql'],
 ['Analytics Marts','Business measures','Python builds reusable sales, customer, inventory, purchasing, and service aggregates from raw CSV extracts, writing aggregates to the processed directory.','etl/build_analytics.py'],
 ['Quality Controls','Checks & reconciliation',`${data.data_quality?.summary?.passed_tests??0} of ${data.data_quality?.summary?.total_tests??0} controls passed in this published run. Checks and reconciliation results are included in the final export; review flags remain visible.`,'validation'],
 ['dashboard.json','Published data contract','The export packages KPI values, monthly series, business findings, quality results, and detail rows into a single JSON file consumed by NorthStar.','web/data/dashboard.json'],
 ['Dashboard','Published intelligence','The exporter writes dashboard.json. GitHub Pages serves the static application, which reads the published export for KPIs, charts, signals, and detail tables.','etl/export_dashboard_data.py']
 ];
 const old=document.querySelector('#architecture .flowline');const box=document.createElement('div');box.className='lineage';
 box.innerHTML=`<p class="lineage-hint">Logical data lineage · select a stage to inspect its role and source</p><div class="lineage-track" role="group" aria-label="Data lineage stages">${stages.map((s,i)=>`<button type="button" class="lineage-node" aria-pressed="${i===0}" aria-controls="lineage-detail" data-stage="${i}"><small>0${i+1}</small><b>${s[0]}</b><span>${s[1]}</span></button>${i<stages.length-1?'<span class="lineage-arrow" aria-hidden="true">→</span>':''}`).join('')}</div><div id="lineage-detail" class="lineage-detail" aria-live="polite"></div>`;
 old.replaceWith(box);
 const select=i=>{box.querySelectorAll('button').forEach((b,j)=>b.setAttribute('aria-pressed',String(i===j)));const s=stages[i];box.querySelector('#lineage-detail').innerHTML=`<span>STAGE 0${i+1} / ${String(stages.length).padStart(2,'0')}</span><h3>${s[0]} · ${s[1]}</h3><p>${h(s[2])}</p>${i===3?starSchemaDetail():''}<a href="https://github.com/Jithendra-data/northstar-distribution-intelligence/tree/main/${s[3]}" target="_blank" rel="noreferrer">View implementation ↗</a>`};
 box.querySelectorAll('button').forEach((button,i)=>{button.addEventListener('click',()=>select(i));button.addEventListener('keydown',event=>{const next=event.key==='ArrowRight'?(i+1)%stages.length:event.key==='ArrowLeft'?(i+stages.length-1)%stages.length:event.key==='Home'?0:event.key==='End'?stages.length-1:null;if(next!==null){event.preventDefault();box.querySelectorAll('button')[next].focus();select(next)}})});select(0);
}

function starSchemaDetail(){
 const root='https://github.com/Jithendra-data/northstar-distribution-intelligence/blob/main/sql/';
 const facts=[['FactSales','One posted invoice line'],['FactInventory','One signed inventory movement'],['FactPurchasing','One purchase order line'],['FactReturns','One return record']];
 const dimensions=['DimDate','DimCustomer','DimProduct','DimVendor','DimSalesRep','DimWarehouse'];
 return `<div class="schema-branch"><div class="schema-hub">Star Schema <span>Transaction facts + descriptive dimensions</span></div><div class="schema-columns"><section><h4>FACTS</h4>${facts.map(([name,grain])=>`<a href="${root}05_facts/facts.sql" target="_blank" rel="noreferrer"><b>dw.${name}</b><small>${grain}</small></a>`).join('')}</section><section><h4>DIMENSIONS</h4>${dimensions.map(name=>`<a href="${root}04_dimensions/dimensions.sql" target="_blank" rel="noreferrer"><b>dw.${name}</b></a>`).join('')}</section></div><div class="schema-destination">↓ Analytics Marts</div><p>Logical model from the SQL definitions. Each fact carries the dimension keys relevant to its grain; the hosted refresh runs through Python and CSV files.</p></div>`;
}
