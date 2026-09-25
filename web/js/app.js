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
    hydrateShell();
    finishLoading();
  }catch(error){document.querySelector('#revenue').textContent='Run export'; console.info(error.message); finishLoading()}
}
function setupFilters(data,k){
  const rows=data.sales_trend_by_region||[],months=[...new Set(rows.map(r=>r.YearMonth))].sort(),region=document.querySelector('#region');
 const kpis=document.querySelector('.kpi-grid');if(!document.querySelector('#yoy'))kpis.insertAdjacentHTML('beforeend','<article class="kpi"><div class="kpi-label">GROSS MARGIN <span>◉</span></div><strong id="gm-kpi">—</strong><small>Gross profit / net revenue</small></article><article class="kpi"><div class="kpi-label">YEAR-OVER-YEAR <span>↗</span></div><strong id="yoy">—</strong><small>Same selected months versus prior year</small></article>');
 const dates=document.createElement('div');dates.className='date-filter';dates.innerHTML=`<label>FROM<select id="date-from"></select></label><label>THROUGH<select id="date-to"></select></label>`;
 document.querySelector('.title-row').insertBefore(dates,document.querySelector('.filter'));
 for(const id of ['date-from','date-to']){const select=dates.querySelector(`#${id}`);select.innerHTML=months.map(m=>`<option value="${h(m)}">${h(m)}</option>`).join('')}
 if(months.length){dates.querySelector('#date-from').value=months[0];dates.querySelector('#date-to').value=months.at(-1)}
 function apply(){
   const from=dates.querySelector('#date-from').value,to=dates.querySelector('#date-to').value,chosen=rows.filter(r=>r.YearMonth>=from&&r.YearMonth<=to&&(region.value==='all'||r.Region===region.value));
   const grouped=new Map();for(const r of chosen){const x=grouped.get(r.YearMonth)||{YearMonth:r.YearMonth,Revenue:0,GrossProfit:0,Units:0,Invoices:0,Orders:0};for(const key of ['Revenue','GrossProfit','Units','Invoices','Orders'])x[key]+=Number(r[key]||0);grouped.set(r.YearMonth,x)}
   const trend=[...grouped.values()].sort((a,b)=>a.YearMonth.localeCompare(b.YearMonth)),rev=trend.reduce((s,x)=>s+x.Revenue,0),gp=trend.reduce((s,x)=>s+x.GrossProfit,0),orderCount=trend.reduce((s,x)=>s+x.Orders,0);
   const toYear=Number(to.slice(0,4)),fromMonth=Number(from.slice(5,7)),toMonth=Number(to.slice(5,7)),samePeriod=rows.filter(r=>Number(r.YearMonth.slice(0,4))===toYear&&Number(r.YearMonth.slice(5,7))>=fromMonth&&Number(r.YearMonth.slice(5,7))<=toMonth&&(region.value==='all'||r.Region===region.value)).reduce((s,r)=>s+Number(r.Revenue||0),0),priorPeriod=rows.filter(r=>Number(r.YearMonth.slice(0,4))===toYear-1&&Number(r.YearMonth.slice(5,7))>=fromMonth&&Number(r.YearMonth.slice(5,7))<=toMonth&&(region.value==='all'||r.Region===region.value)).reduce((s,r)=>s+Number(r.Revenue||0),0),yoy=priorPeriod?(samePeriod-priorPeriod)/priorPeriod:null;
   document.querySelector('#revenue').textContent=money(rev);document.querySelector('#profit').textContent=money(gp);document.querySelector('#margin').textContent=`${(rev?gp/rev*100:0).toFixed(1)}%`;document.querySelector('#gm-kpi').textContent=`${(rev?gp/rev*100:0).toFixed(1)}%`;document.querySelector('#yoy').textContent=yoy==null?'—':`${yoy>=0?'+':''}${(yoy*100).toFixed(1)}%`;document.querySelector('#orders').textContent=integer(orderCount);document.querySelector('.period').textContent=`${from} — ${to}`;drawCharts(trend);
 }
 dates.addEventListener('change',apply);region.addEventListener('change',apply);apply();
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
 el.innerHTML=`<div class="finding-heading"><span>CALCULATED FROM THIS DATASET</span><b>Signals to investigate</b></div><div class="finding-cards">${cards.map(c=>`<article><small>${c[0]}</small><strong>${c[1]}</strong><p>${c[2]}</p></article>`).join('')}</div>`;
 document.querySelector('.chart-grid').insertAdjacentElement('afterend',el);
}
function renderQuality(q){
 const section=document.querySelector('#quality'),s=q.summary||{}; if(!section)return;
 const passed=Number(s.passed_tests||0),failed=Number(s.failed_tests||0),tests=q.results||[];
 section.querySelector('p').textContent=`${integer(s.total_tests||0)} automated controls reviewed for this synthetic run. ${integer(s.failed_records||0)} ending inventory position(s) are flagged for scenario investigation.`;
 const table=document.createElement('div');table.className='quality-list';
 table.innerHTML=tests.map(t=>`<div class="quality-row"><span>${t.TestName}</span><b class="${t.Status==='PASS'?'pass':'fail'}">${t.Status==='PASS'?'OK':'REVIEW'}</b><small>${integer(t.FailedRecords)} flagged / ${integer(t.RecordsChecked)} checked</small></div>`).join('');
 section.appendChild(table);
 const nav=document.querySelector('.sidebar nav');
 nav.insertAdjacentHTML('beforeend','<a href="#architecture"><i>⌘</i>Architecture</a><a href="#documentation"><i>▧</i>Documentation</a>');
 section.insertAdjacentHTML('afterend',`<section class="placeholder-section" id="architecture"><span>07 / SYSTEM DESIGN</span><h2>From synthetic ERP to business decisions</h2><div class="flowline"><b>Synthetic ERP</b><i>→</i><b>Raw CSV</b><i>→</i><b>Staging</b><i>→</i><b>Star schema</b><i>→</i><b>Analytics marts</b><i>→</i><b>Static JSON</b><i>→</i><b>Dashboard</b></div><p>Raw preserves source records. Staging standardizes and checks them. The warehouse models conformed dimensions and transaction-grain facts. Marts define business measures, quality controls check relationships and totals, and the static dashboard reads only precomputed files.</p></section><section class="placeholder-section" id="documentation"><span>08 / PROJECT DOCUMENTATION</span><h2>Methods, definitions, and operating notes</h2><div class="doc-links"><a href="https://github.com/Jithendra-data/northstar-distribution-intelligence/blob/main/documentation/requirements/business_requirements.md" target="_blank" rel="noreferrer">Business requirements ↗</a><a href="https://github.com/Jithendra-data/northstar-distribution-intelligence/blob/main/documentation/architecture/architecture.md" target="_blank" rel="noreferrer">Architecture &amp; ER model ↗</a><a href="https://github.com/Jithendra-data/northstar-distribution-intelligence/blob/main/documentation/data_dictionary/data_dictionary.md" target="_blank" rel="noreferrer">Data dictionary ↗</a><a href="https://github.com/Jithendra-data/northstar-distribution-intelligence/blob/main/documentation/kpi_dictionary/kpi_dictionary.md" target="_blank" rel="noreferrer">KPI definitions ↗</a><a href="https://github.com/Jithendra-data/northstar-distribution-intelligence/blob/main/testing/validation_strategy.md" target="_blank" rel="noreferrer">Control strategy ↗</a><a href="https://github.com/Jithendra-data/northstar-distribution-intelligence/blob/main/case-study/case_study.md" target="_blank" rel="noreferrer">Case study ↗</a></div></section>`);
}
const h=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function finishLoading(){
 document.querySelector('.loader')?.setAttribute('aria-hidden','true');
 document.body.classList.remove('is-loading');
 if(prefersReducedMotion){document.body.classList.remove('reveal-ready');return}
 requestAnimationFrame(()=>{
  const targets='.portfolio-story,.kpi,.panel,.finding-grid,.explore,.placeholder-section';
  if(window.gsap){
   gsap.to(targets,{opacity:1,y:0,duration:.58,ease:'power3.out',stagger:.035,onComplete:()=>document.body.classList.remove('reveal-ready')});
  }else{
   document.body.classList.remove('reveal-ready');
  }
 });
}
function hydrateShell(){
 const links=[...document.querySelectorAll('.sidebar nav a[href^="#"]')];
 const sections=links.map(a=>document.querySelector(a.getAttribute('href'))).filter(Boolean);
 const setActive=id=>links.forEach(a=>a.classList.toggle('active',a.getAttribute('href')===`#${id}`));
 links.forEach(a=>a.addEventListener('click',()=>setActive(a.getAttribute('href').slice(1))));
 if('IntersectionObserver' in window){
  const observer=new IntersectionObserver(entries=>{
   const visible=entries.filter(entry=>entry.isIntersecting).sort((a,b)=>b.intersectionRatio-a.intersectionRatio)[0];
   if(visible) setActive(visible.target.id);
  },{rootMargin:'-18% 0px -70% 0px',threshold:[.05,.2,.45]});
  sections.forEach(section=>observer.observe(section));
 }
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
   const box=document.createElement('article');box.className='data-table-card';box.innerHTML=`<div class="table-head"><h3>${h(title)}</h3><div><input type="search" placeholder="Search rows…" aria-label="Search ${h(title)}"><button type="button" class="csv-button">Download CSV</button></div></div><div class="table-scroll"><table><thead><tr>${columns.map((c,i)=>`<th data-col="${i}">${h(c[1])} <span>↕</span></th>`).join('')}</tr></thead><tbody></tbody></table></div><div class="table-pager"><button type="button" class="previous">Previous</button><small></small><button type="button" class="next">Next</button></div>`;
   section.appendChild(box); let page=0, allRows=[...rows], filtered=allRows;const size=40,tbody=box.querySelector('tbody'),status=box.querySelector('.table-pager small');
   function draw(){const pages=Math.max(1,Math.ceil(filtered.length/size));page=Math.min(page,pages-1);tbody.innerHTML=filtered.slice(page*size,(page+1)*size).map(row=>`<tr>${columns.map(c=>{let v=row[c[0]];if(c[2]==='money')v=money(Number(v));else if(c[2]==='percent')v=`${(Number(v)*100).toFixed(1)}%`;else if(c[2]==='number'&&v!=null)v=integer(Number(v));return `<td>${h(v==null?'—':v)}</td>`}).join('')}</tr>`).join('');status.textContent=`${filtered.length? page*size+1:0}–${Math.min((page+1)*size,filtered.length)} of ${filtered.length}`;box.querySelector('.previous').disabled=page===0;box.querySelector('.next').disabled=page>=pages-1;}
   box.querySelector('input').addEventListener('input',e=>{const q=e.target.value.toLowerCase();filtered=allRows.filter(row=>Object.values(row).some(v=>String(v??'').toLowerCase().includes(q)));page=0;draw()});
   box.querySelector('.previous').addEventListener('click',()=>{page--;draw()});box.querySelector('.next').addEventListener('click',()=>{page++;draw()});
   box.querySelectorAll('th').forEach(th=>th.addEventListener('click',()=>{const c=columns[Number(th.dataset.col)][0],asc=th.dataset.direction!=='asc';th.dataset.direction=asc?'asc':'desc';filtered=[...filtered].sort((a,b)=>{const cmp=String(a[c]??'').localeCompare(String(b[c]??''),undefined,{numeric:true});return asc?cmp:-cmp});draw()}));
   box.querySelector('.csv-button').addEventListener('click',()=>{const csv=[columns.map(c=>'"'+c[1].replaceAll('"','""')+'"').join(','),...filtered.map(row=>columns.map(c=>'"'+String(row[c[0]]??'').replaceAll('"','""')+'"').join(','))].join('\r\n');const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));a.download=`northstar-detail-${index+1}.csv`;a.click();URL.revokeObjectURL(a.href)});
   draw();
 });
}
function drawCharts(rows){
 if(!window.echarts)return;
 const trendDom=document.querySelector('#trend'),marginDom=document.querySelector('#margin-chart'),trend=echarts.getInstanceByDom(trendDom)||echarts.init(trendDom),margin=echarts.getInstanceByDom(marginDom)||echarts.init(marginDom);
 const months=rows.map(x=>x.YearMonth), revenues=rows.map(x=>x.Revenue), profits=rows.map(x=>x.GrossProfit), margins=rows.map(x=>x.GrossMarginPct*100);
 const base={tooltip:{trigger:'axis',backgroundColor:'#173549',borderWidth:0,textStyle:{color:'#fff'}},grid:{left:42,right:18,top:20,bottom:35},xAxis:{type:'category',data:months,axisLabel:{color:'#82929b',fontSize:9},axisLine:{lineStyle:{color:'#e7edef'}},axisTick:{show:false}},yAxis:{type:'value',axisLabel:{color:'#82929b',fontSize:9,formatter:v=>`$${integer(v)}`},splitLine:{lineStyle:{color:'#eef2f3',type:'dashed'}}}};
 trend.setOption({...base,legend:{bottom:0,textStyle:{fontSize:10,color:'#71828b'}},series:[{name:'Revenue',type:'line',smooth:true,data:revenues,symbol:'none',lineStyle:{width:2.5,color:'#2b9b8c'},areaStyle:{color:'rgba(43,155,140,.10)'}},{name:'Gross profit',type:'line',smooth:true,data:profits,symbol:'none',lineStyle:{width:2,color:'#5487dc'}}]},true);
 margin.setOption({tooltip:{trigger:'axis'},grid:{left:40,right:16,top:18,bottom:35},xAxis:{type:'category',data:months,axisLabel:{color:'#82929b',fontSize:9},axisLine:{lineStyle:{color:'#e7edef'}},axisTick:{show:false}},yAxis:{type:'value',axisLabel:{color:'#82929b',fontSize:9,formatter:'{value}%'},splitLine:{lineStyle:{color:'#eef2f3',type:'dashed'}}},series:[{type:'line',smooth:true,data:margins,symbol:'none',lineStyle:{width:2.5,color:'#d5a844'},areaStyle:{color:'rgba(213,168,68,.12)'}}]},true);
 if(!window.__northstarResizeBound){window.addEventListener('resize',()=>{echarts.getInstanceByDom(document.querySelector('#trend'))?.resize();echarts.getInstanceByDom(document.querySelector('#margin-chart'))?.resize()});window.__northstarResizeBound=true}
}
loadDashboard();

