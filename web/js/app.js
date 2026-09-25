const money = value => new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',notation:value>=1e6?'compact':'standard',maximumFractionDigits:1}).format(value||0);
const integer = value => new Intl.NumberFormat('en-US',{notation:'compact',maximumFractionDigits:1}).format(value||0);
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
document.body.classList.add('reveal-ready');
async function loadDashboard(){
  try{
    const cacheKey=location.search||`?v=${Date.now()}`;
    const response=await fetch(`data/dashboard.json${cacheKey}`); if(!response.ok) throw new Error('Dashboard export is not available yet.');
    const data=await response.json(),k=data.executive_kpis||{};
    const run=data.pipeline_metadata||{};
    const banner=document.querySelector('.notice');
    if(banner&&run.refreshed_at_utc){const refreshed=new Date(run.refreshed_at_utc).toLocaleString();banner.textContent=`Synthetic scenario · seed ${run.random_seed} · refreshed ${refreshed}. Figures are fictional and intended for analytics demonstration.`}
    document.querySelector('.hero-status small').textContent=run.random_seed?`Seed ${run.random_seed} · refreshed by GitHub Actions`:'Generate, check, reconcile, deploy';
    document.querySelector('#customers-kpi').textContent=integer(k.customers); document.querySelector('#inventory-kpi').textContent=money(k.inventory_value); document.querySelector('#po-value').textContent=money(k.open_po_value);
    setupFilters(data,k);
    renderFindings(data.business_findings||{});
    renderQuality(data.data_quality||{});
    renderTables(data);
    renderExecutiveSignals(data);
    renderLineage(data);
    setupProjectPage(data);
    hydrateShell();
    finishLoading();
  }catch(error){document.querySelector('#revenue').textContent='Run export'; console.info(error.message); finishLoading()}
}
function setupFilters(data,k){
  const rows=data.sales_trend_by_region||[],months=[...new Set(rows.map(r=>r.YearMonth))].sort(),region=document.querySelector('#region');
 const kpis=document.querySelector('.kpi-grid');if(!document.querySelector('#yoy'))kpis.insertAdjacentHTML('beforeend','<article class="kpi"><div class="kpi-label">GROSS MARGIN <span>◉</span></div><strong id="gm-kpi">—</strong><small>Gross profit / net revenue</small></article><article class="kpi"><div class="kpi-label">YEAR-OVER-YEAR <span>↗</span></div><strong id="yoy">—</strong><small>Same selected months versus prior year</small></article>');
 const dates=document.createElement('div');dates.className='date-filter';dates.innerHTML=`<label>FROM<select id="date-from"></select></label><label>THROUGH<select id="date-to"></select></label>`;
 const toolbar=document.createElement('div');toolbar.className='filter-toolbar';toolbar.setAttribute('aria-label','Financial performance filters');
 document.querySelector('.hero-copy').appendChild(toolbar);toolbar.append(dates,document.querySelector('.filter'));toolbar.insertAdjacentHTML('beforeend','<span class="filter-scope">Filters apply to financial KPIs and charts. Operational metrics and detail tables show the full dataset.</span>');
 for(const id of ['date-from','date-to']){const select=dates.querySelector(`#${id}`);select.innerHTML=months.map(m=>`<option value="${h(m)}">${h(m)}</option>`).join('')}
 if(months.length){dates.querySelector('#date-from').value=months[0];dates.querySelector('#date-to').value=months.at(-1)}
 function apply(){
   const from=dates.querySelector('#date-from').value,to=dates.querySelector('#date-to').value,chosen=rows.filter(r=>r.YearMonth>=from&&r.YearMonth<=to&&(region.value==='all'||r.Region===region.value));
   const grouped=new Map();for(const r of chosen){const x=grouped.get(r.YearMonth)||{YearMonth:r.YearMonth,Revenue:0,GrossProfit:0,Units:0,Invoices:0,Orders:0};for(const key of ['Revenue','GrossProfit','Units','Invoices','Orders'])x[key]+=Number(r[key]||0);grouped.set(r.YearMonth,x)}
   const trend=[...grouped.values()].sort((a,b)=>a.YearMonth.localeCompare(b.YearMonth)),rev=trend.reduce((s,x)=>s+x.Revenue,0),gp=trend.reduce((s,x)=>s+x.GrossProfit,0),orderCount=trend.reduce((s,x)=>s+x.Orders,0);
   const toYear=Number(to.slice(0,4)),fromMonth=Number(from.slice(5,7)),toMonth=Number(to.slice(5,7)),samePeriod=rows.filter(r=>Number(r.YearMonth.slice(0,4))===toYear&&Number(r.YearMonth.slice(5,7))>=fromMonth&&Number(r.YearMonth.slice(5,7))<=toMonth&&(region.value==='all'||r.Region===region.value)).reduce((s,r)=>s+Number(r.Revenue||0),0),priorPeriod=rows.filter(r=>Number(r.YearMonth.slice(0,4))===toYear-1&&Number(r.YearMonth.slice(5,7))>=fromMonth&&Number(r.YearMonth.slice(5,7))<=toMonth&&(region.value==='all'||r.Region===region.value)).reduce((s,r)=>s+Number(r.Revenue||0),0),yoy=priorPeriod?(samePeriod-priorPeriod)/priorPeriod:null;
   document.querySelector('#revenue').textContent=money(rev);document.querySelector('#profit').textContent=money(gp);document.querySelector('#margin').textContent=`${(rev?gp/rev*100:0).toFixed(1)}%`;document.querySelector('#gm-kpi').textContent=`${(rev?gp/rev*100:0).toFixed(1)}%`;document.querySelector('#yoy').textContent=yoy==null?'—':`${yoy>=0?'+':''}${(yoy*100).toFixed(1)}%`;document.querySelector('#orders').textContent=integer(orderCount);document.querySelector('.period').textContent=`${from} — ${to}`;drawCharts(trend);renderMetricContext(trend,from,to,region.value);polishKpis(data,trend,from,to,region.value);
 }
 dates.addEventListener('change',apply);region.addEventListener('change',apply);apply();
}
function renderMetricContext(rows,from,to,region){
 const last=rows.at(-1),previous=rows.at(-2);
 const contexts={revenue:['Revenue',false],profit:['GrossProfit',false],orders:['Orders',false],'gm-kpi':['margin',true]};
 for(const [id,[field,isMargin]] of Object.entries(contexts)){
  const card=document.getElementById(id).closest('.kpi');let context=card.querySelector('.kpi-context');
  if(!context){context=document.createElement('div');context.className='kpi-context';card.appendChild(context)}
  const value=row=>isMargin?(row.Revenue?row.GrossProfit/row.Revenue*100:0):row[field];
  const delta=last&&previous?(isMargin?value(last)-value(previous):(value(previous)?(value(last)-value(previous))/value(previous)*100:null)):null;
  context.innerHTML=delta==null?'<span class="trend-badge neutral">No prior month</span>':`<span class="trend-badge ${delta<0?'down':''}">${delta>=0?'+':''}${delta.toFixed(1)}${isMargin?' pp':'%'}</span><span>${h(last.YearMonth)} vs ${h(previous.YearMonth)}</span>`;
 }
 for(const id of ['customers-kpi','inventory-kpi','po-value']){const card=document.getElementById(id).closest('.kpi');if(!card.querySelector('.kpi-context'))card.insertAdjacentHTML('beforeend','<div class="kpi-context"><span class="trend-badge neutral">Full dataset</span><span>All regions</span></div>')}
 document.querySelector('#trend-summary').textContent=`${rows.length} monthly observations · ${region==='all'?'All regions':region} · ${from} to ${to}`;
 document.querySelector('#margin-summary').textContent=last?`Latest month · ${last.YearMonth} · ${(last.Revenue?last.GrossProfit/last.Revenue*100:0).toFixed(1)}% gross margin`:'No observations in this selection';
}
function renderFindings(f){
 const el=document.createElement('section'); el.className='finding-grid';
 const v=f.vendor_one_average_actual_lead_days_by_year||{}, years=Object.keys(v).sort(), snacks=f.snacks_discount_and_margin_by_year||{}, sy=Object.keys(snacks).sort();
 const first=snacks[sy[0]]||{},last=snacks[sy.at(-1)]||{};
 const cards=[
  ['SUPPLIER RELIABILITY',`${v[years[0]]??'—'} → ${v[years.at(-1)]??'—'} days`,`Vendor V0001 actual receipt lead time by year`],
  ['WAREHOUSE SERVICE',`${(f.warehouse_average_ship_days||{}).ATL??'—'} days`,`Atlanta average order-to-ship time`],
  ['INVENTORY EXPOSURE',`${integer(f.critical_stockout_sku_warehouse_rows)} critical rows`,`Dead inventory at ${money(f.dead_inventory_value)}`],
  ['CUSTOMER RETENTION',`${integer(f.valuable_customers_inactive_over_60_days)} accounts`,`Over $25K lifetime revenue and 60+ days inactive`],
  ['DISCOUNT & MARGIN',`${((last.discount_rate||0)*100).toFixed(1)}% discount`,`Snacks margin ${((first.gross_margin||0)*100).toFixed(1)}% → ${((last.gross_margin||0)*100).toFixed(1)}%`],
  ['PRODUCT QUALITY',`${((f.health_2025_return_amount_rate||0)*100).toFixed(1)}% returns`,`Health return amount as a share of 2025 revenue`]
 ];
 el.innerHTML=`<div class="finding-heading"><span>FULL DATASET · INVESTIGATION SIGNALS</span><b>Business observations</b></div><div class="finding-cards">${cards.map((c,i)=>`<article><small>${c[0]}</small><strong>${c[1]}</strong><p>${c[2]}</p><a class="insight-link" href="#${['purchasing','operations','inventory','customers','sales','operations'][i]}">Investigate signal <span aria-hidden="true">→</span></a></article>`).join('')}</div>`;
 document.querySelector('.chart-grid').insertAdjacentElement('afterend',el);
}
function renderQuality(q){
 const section=document.querySelector('#quality'),s=q.summary||{}; if(!section)return;
 const passed=Number(s.passed_tests||0),failed=Number(s.failed_tests||0),tests=q.results||[];
 section.querySelector('p').textContent=`${integer(s.total_tests||0)} automated controls reviewed for this synthetic run. ${integer(s.failed_records||0)} ending inventory position(s) are flagged for scenario investigation.`;
 const table=document.createElement('div');table.className='quality-list';
 table.innerHTML=tests.map(t=>`<div class="quality-row"><span>${t.TestName}</span><b class="${t.Status==='PASS'?'pass':'fail'}">${t.Status==='PASS'?'OK':'REVIEW'}</b><small>${integer(t.FailedRecords)} flagged / ${integer(t.RecordsChecked)} checked</small></div>`).join('');
 section.appendChild(table);

 section.insertAdjacentHTML('afterend',`<section class="placeholder-section" id="architecture"><span>07 / SYSTEM DESIGN</span><h2>From synthetic ERP to business decisions</h2><div class="flowline"><b>Synthetic ERP</b><i>→</i><b>Raw CSV</b><i>→</i><b>Staging</b><i>→</i><b>Star schema</b><i>→</i><b>Analytics marts</b><i>→</i><b>Static JSON</b><i>→</i><b>Dashboard</b></div><p>Raw preserves source records. Staging standardizes and checks them. The warehouse models conformed dimensions and transaction-grain facts. Marts define business measures, quality controls check relationships and totals, and the static dashboard reads only precomputed files.</p></section><section class="placeholder-section" id="documentation"><span>08 / PROJECT DOCUMENTATION</span><h2>Methods, definitions, and operating notes</h2><div class="doc-links"><a href="https://github.com/Jithendra-data/northstar-distribution-intelligence/blob/main/documentation/requirements/business_requirements.md" target="_blank" rel="noreferrer">Business requirements ↗</a><a href="https://github.com/Jithendra-data/northstar-distribution-intelligence/blob/main/documentation/architecture/architecture.md" target="_blank" rel="noreferrer">Architecture &amp; ER model ↗</a><a href="https://github.com/Jithendra-data/northstar-distribution-intelligence/blob/main/documentation/data_dictionary/data_dictionary.md" target="_blank" rel="noreferrer">Data dictionary ↗</a><a href="https://github.com/Jithendra-data/northstar-distribution-intelligence/blob/main/documentation/kpi_dictionary/kpi_dictionary.md" target="_blank" rel="noreferrer">KPI definitions ↗</a><a href="https://github.com/Jithendra-data/northstar-distribution-intelligence/blob/main/testing/validation_strategy.md" target="_blank" rel="noreferrer">Control strategy ↗</a><a href="https://github.com/Jithendra-data/northstar-distribution-intelligence/blob/main/case-study/case_study.md" target="_blank" rel="noreferrer">Case study ↗</a></div></section>`);
}
const h=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function drawFallbackLineChart(dom, labels, series, options={}){
 if(!dom)return;
 const width=Math.max(320,dom.clientWidth||320),height=Math.max(220,dom.clientHeight||220),pad={top:18,right:18,bottom:34,left:42};
 const flat=series.flatMap(s=>s.data).filter(v=>Number.isFinite(Number(v))).map(Number);
 dom.innerHTML='';
 if(!labels.length||!flat.length){dom.innerHTML='<div class="chart-empty">No chart data for the selected filters.</div>';return}
 let min=Math.min(...flat),max=Math.max(...flat); if(min===max){min=min*.95;max=max*1.05}
 if(options.zeroBase)min=Math.min(0,min);
 const x=i=>labels.length===1?pad.left+(width-pad.left-pad.right)/2:pad.left+(i/(labels.length-1))*(width-pad.left-pad.right);
 const y=v=>height-pad.bottom-((Number(v)-min)/(max-min||1))*(height-pad.top-pad.bottom);
 const ticks=[0,.5,1].map(r=>min+(max-min)*r);
 const linePath=data=>data.map((v,i)=>`${i?'L':'M'} ${x(i).toFixed(1)} ${y(v).toFixed(1)}`).join(' ');
 const areaPath=data=>`${linePath(data)} L ${x(data.length-1).toFixed(1)} ${height-pad.bottom} L ${x(0).toFixed(1)} ${height-pad.bottom} Z`;
 const grid=ticks.map(t=>`<g><line x1="${pad.left}" x2="${width-pad.right}" y1="${y(t).toFixed(1)}" y2="${y(t).toFixed(1)}" stroke="#eef2f3" stroke-dasharray="4 4"/><text x="${pad.left-8}" y="${(y(t)+4).toFixed(1)}" text-anchor="end" fill="#82929b" font-size="9">${options.format?options.format(t):integer(t)}</text></g>`).join('');
 const monthLabels=labels.filter((_,i)=>i===0||i===labels.length-1||i%6===0).map(label=>{const i=labels.indexOf(label);return `<text x="${x(i).toFixed(1)}" y="${height-12}" text-anchor="middle" fill="#82929b" font-size="9">${h(label)}</text>`}).join('');
 const paths=series.map((s,i)=>`<path d="${areaPath(s.data)}" fill="${s.fill||'transparent'}"/><path d="${linePath(s.data)}" fill="none" stroke="${s.color}" stroke-width="${i?2:2.5}" stroke-linecap="round" stroke-linejoin="round"/>`).join('');
 dom.innerHTML=`<svg viewBox="0 0 ${width} ${height}" width="100%" height="100%" role="img" aria-label="${h(options.label||'Line chart')}">${grid}${monthLabels}${paths}</svg>`;
}
function drawFallbackCharts(rows){
 const months=rows.map(x=>x.YearMonth), revenues=rows.map(x=>Number(x.Revenue)||0), profits=rows.map(x=>Number(x.GrossProfit)||0), margins=rows.map(x=>{const revenue=Number(x.Revenue)||0,profit=Number(x.GrossProfit)||0,stored=Number(x.GrossMarginPct);return Number.isFinite(stored)?stored*100:(revenue?profit/revenue*100:null)});
 drawFallbackLineChart(document.querySelector('#trend'),months,[{data:revenues,color:'#2b9b8c',fill:'rgba(43,155,140,.10)'},{data:profits,color:'#5487dc',fill:'transparent'}],{label:'Revenue and gross profit trend',zeroBase:true,format:v=>`${integer(v)}`});
 drawFallbackLineChart(document.querySelector('#margin-chart'),months,[{data:margins,color:'#d5a844',fill:'rgba(213,168,68,.12)'}],{label:'Gross margin percentage trend',format:v=>`${Number(v).toFixed(1)}%`});
}
function finishLoading(){
 document.querySelector('.loader')?.setAttribute('aria-hidden','true');
 document.body.classList.remove('is-loading');
 if(prefersReducedMotion){document.body.classList.remove('reveal-ready');return}
 requestAnimationFrame(()=>{
  const targets='.portfolio-story,.kpi,.panel,.finding-grid,.explore,.placeholder-section';
  if(window.gsap){
   gsap.to(targets,{opacity:1,y:0,duration:.35,ease:'power3.out',stagger:.015,onComplete:()=>document.body.classList.remove('reveal-ready')});
  }else{
   document.body.classList.remove('reveal-ready');
  }
 });
}
function hydrateShell(){
 const links=[...document.querySelectorAll('.sidebar nav a[href^="#"]')];
 const sections=links.map(a=>document.querySelector(a.getAttribute('href'))).filter(Boolean);
 const setActive=id=>links.forEach(a=>{const active=a.getAttribute('href')===`#${id}`;a.classList.toggle('active',active);if(active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');if(active)document.querySelector('.crumb').textContent=`NorthStar / ${a.textContent.slice(1).trim()}`});
 const nav=document.querySelector('.sidebar nav');nav.appendChild(nav.querySelector('[href="#project-story"]'));
 nav.querySelector('[href="#sales"]').insertAdjacentHTML('beforebegin','<div class="nav-group">ANALYTICS</div>');
 nav.querySelector('[href="#quality"]').insertAdjacentHTML('beforebegin','<div class="nav-group">ENGINEERING</div>');
 setActive(['#architecture','#documentation'].includes(location.hash)?'project-story':location.hash.slice(1)||'overview');
 links.forEach(a=>a.addEventListener('click',()=>setActive(a.getAttribute('href').slice(1))));
 let queued=false;
 const updateNavigation=()=>{queued=false;const current=sections.filter(section=>section.getClientRects().length&&section.getBoundingClientRect().top<=130).sort((a,b)=>b.getBoundingClientRect().top-a.getBoundingClientRect().top)[0];setActive(current?.id||'overview')};
 window.addEventListener('scroll',()=>{if(!queued){queued=true;requestAnimationFrame(updateNavigation)}},{passive:true});

}
function renderTables(data){
 const specs=[
  ['#sales','Category revenue and margin',data.sales_by_category,[['CategoryName','Category'],['Revenue','Revenue','money'],['GrossProfit','Gross profit','money'],['GrossMarginPct','Gross margin','percent'],['Units','Units','number']]],
  ['#customers','Customer value and recency',data.customer_performance,[['CustomerName','Customer'],['Region','Region'],['CustomerGroup','Group'],['LifetimeRevenue','Lifetime revenue','money'],['LastPurchaseDate','Last purchase'],['DaysInactive','Days inactive','number'],['Segment','Segment']]],
  ['#inventory','SKU availability and stock risk',data.inventory_detail,[['SKU','SKU'],['ProductName','Product'],['CategoryName','Category'],['WarehouseID','Warehouse'],['AvailableQty','Available qty','number'],['Sales30Day','30-day sales','number'],['Sales90Day','90-day sales','number'],['DaysOnHand','Days on hand','number'],['InboundQty','Inbound','number'],['RiskLevel','Risk']]],
  ['#purchasing','Outstanding purchase commitments',data.open_purchase_orders,[['PONumber','PO'],['VendorName','Vendor'],['ExpectedDeliveryDate','Expected'],['DaysLate','Days late','number'],['RemainingQuantity','Remaining qty','number'],['RemainingValue','Remaining value','money']]],
  ['#purchasing','Vendor delivery and fill',data.vendor_performance,[['VendorID','Vendor ID'],['POCount','PO count','number'],['OrderedQuantity','Ordered qty','number'],['ReceivedQuantity','Received qty','number'],['FillRate','Fill rate','percent'],['POValue','PO value','money']]],
  ['#operations','Warehouse service performance',data.warehouse_performance,[['WarehouseID','Warehouse'],['AvgOrderToShipDays','Avg ship days','number'],['ShippedOrders','Orders shipped','number'],['Backorders','Backorders','number']]],
  ['#operations','Customer return reasons',data.returns_by_reason,[['ReturnReason','Reason'],['Returns','Return lines','number'],['ReturnAmount','Return amount','money']]],
  ['#sales','Top invoiced sales lines',data.sales_detail,[['InvoiceDate','Invoice date'],['CustomerID','Customer'],['Region','Region'],['SKU','SKU'],['ProductName','Product'],['CategoryName','Category'],['Channel','Channel'],['Quantity','Units','number'],['Revenue','Revenue','money'],['DiscountAmount','Discount','money'],['GrossProfit','Gross profit','money']]]
 ];
 specs.forEach(([selector,title,rows,columns],index)=>{
   const section=document.querySelector(selector); if(!section||!Array.isArray(rows)||!rows.length)return;
   const box=document.createElement('article');box.className='data-table-card';box.innerHTML=`<div class="table-head"><h3>${h(title)}</h3><div><input type="search" placeholder="Search rows…" aria-label="Search ${h(title)}"><button type="button" class="csv-button">Download CSV</button></div></div><div class="table-scroll"><table><thead><tr>${columns.map((c,i)=>`<th data-col="${i}" scope="col" aria-sort="none"><button class="sort-button" type="button">${h(c[1])} <span aria-hidden="true">↕</span></button></th>`).join('')}</tr></thead><tbody></tbody></table></div><div class="table-pager"><button type="button" class="previous">Previous</button><small></small><button type="button" class="next">Next</button></div>`;
   section.appendChild(box); let page=0, allRows=[...rows], filtered=allRows;const size=40,tbody=box.querySelector('tbody'),status=box.querySelector('.table-pager small');
   function draw(){const pages=Math.max(1,Math.ceil(filtered.length/size));page=Math.min(page,pages-1);tbody.innerHTML=filtered.slice(page*size,(page+1)*size).map(row=>`<tr>${columns.map(c=>{let v=row[c[0]];if(c[2]==='money')v=money(Number(v));else if(c[2]==='percent')v=`${(Number(v)*100).toFixed(1)}%`;else if(c[2]==='number'&&v!=null)v=integer(Number(v));return `<td>${h(v==null?'—':v)}</td>`}).join('')}</tr>`).join('');if(!filtered.length)tbody.innerHTML=`<tr><td class="table-empty" colspan="${columns.length}">No matching records. Try another search.</td></tr>`;status.textContent=`${filtered.length? page*size+1:0}–${Math.min((page+1)*size,filtered.length)} of ${filtered.length}`;box.querySelector('.previous').disabled=page===0;box.querySelector('.next').disabled=page>=pages-1;}
   box.querySelector('input').addEventListener('input',e=>{const q=e.target.value.toLowerCase();filtered=allRows.filter(row=>Object.values(row).some(v=>String(v??'').toLowerCase().includes(q)));page=0;draw()});
   box.querySelector('.previous').addEventListener('click',()=>{page--;draw()});box.querySelector('.next').addEventListener('click',()=>{page++;draw()});
   box.querySelectorAll('th').forEach(th=>th.querySelector('button').addEventListener('click',()=>{const c=columns[Number(th.dataset.col)][0],asc=th.dataset.direction!=='asc';box.querySelectorAll('th').forEach(header=>header.setAttribute('aria-sort','none'));th.setAttribute('aria-sort',asc?'ascending':'descending');th.dataset.direction=asc?'asc':'desc';filtered=[...filtered].sort((a,b)=>{const cmp=String(a[c]??'').localeCompare(String(b[c]??''),undefined,{numeric:true});return asc?cmp:-cmp});draw()}));
   box.querySelector('.csv-button').addEventListener('click',()=>{const csv=[columns.map(c=>'"'+c[1].replaceAll('"','""')+'"').join(','),...filtered.map(row=>columns.map(c=>'"'+String(row[c[0]]??'').replaceAll('"','""')+'"').join(','))].join('\r\n');const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));a.download=`northstar-detail-${index+1}.csv`;a.click();URL.revokeObjectURL(a.href)});
   draw();
 });
}
function drawCharts(rows){
 if(!window.echarts){drawFallbackCharts(rows);return;}
 const trendDom=document.querySelector('#trend'),marginDom=document.querySelector('#margin-chart'),trend=echarts.getInstanceByDom(trendDom)||echarts.init(trendDom),margin=echarts.getInstanceByDom(marginDom)||echarts.init(marginDom);
 const months=rows.map(x=>x.YearMonth), revenues=rows.map(x=>Number(x.Revenue)||0), profits=rows.map(x=>Number(x.GrossProfit)||0), margins=rows.map(x=>{const revenue=Number(x.Revenue)||0,profit=Number(x.GrossProfit)||0,stored=Number(x.GrossMarginPct);return Number.isFinite(stored)?stored*100:(revenue?profit/revenue*100:null)});
 const base={animation:!prefersReducedMotion,animationDuration:300,aria:{enabled:true},tooltip:{trigger:'axis',backgroundColor:'#173549',borderWidth:0,textStyle:{color:'#fff'}},grid:{left:12,right:18,top:20,bottom:42,containLabel:true},xAxis:{type:'category',data:months,axisLabel:{color:'#596b7a',fontSize:11},axisLine:{lineStyle:{color:'#e7edef'}},axisTick:{show:false}},yAxis:{type:'value',axisLabel:{color:'#596b7a',fontSize:11,formatter:v=>`$${integer(v)}`},splitLine:{lineStyle:{color:'#eef2f3',type:'dashed'}}}};
 trend.setOption({...base,legend:{bottom:0,textStyle:{fontSize:10,color:'#71828b'}},series:[{name:'Revenue',type:'line',smooth:true,data:revenues,symbol:'none',lineStyle:{width:2.5,color:'#2b9b8c'},areaStyle:{color:'rgba(43,155,140,.10)'}},{name:'Gross profit',type:'line',smooth:true,data:profits,symbol:'none',lineStyle:{width:2,color:'#5487dc'}}]},true);
 margin.setOption({animation:!prefersReducedMotion,animationDuration:300,aria:{enabled:true},tooltip:{...base.tooltip,valueFormatter:value=>`${Number(value).toFixed(2)}%`},grid:{left:12,right:16,top:18,bottom:35,containLabel:true},xAxis:{type:'category',data:months,axisLabel:{color:'#596b7a',fontSize:11},axisLine:{lineStyle:{color:'#e7edef'}},axisTick:{show:false}},yAxis:{type:'value',axisLabel:{color:'#596b7a',fontSize:11,formatter:'{value}%'},splitLine:{lineStyle:{color:'#eef2f3',type:'dashed'}}},series:[{name:'Gross margin',type:'line',smooth:true,data:margins,symbol:'none',lineStyle:{width:2.5,color:'#d5a844'},areaStyle:{color:'rgba(213,168,68,.12)'}}]},true);
 if(!window.__northstarResizeBound){window.addEventListener('resize',()=>{echarts.getInstanceByDom(document.querySelector('#trend'))?.resize();echarts.getInstanceByDom(document.querySelector('#margin-chart'))?.resize()});window.__northstarResizeBound=true}
}
loadDashboard();

