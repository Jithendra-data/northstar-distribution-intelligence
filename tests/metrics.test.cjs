const {test}=require('node:test');const assert=require('node:assert/strict');const {reportingPeriod}=require('../web/js/metrics.js');
const rows=[];for(let year=2023;year<=2025;year++)for(let month=1;month<=12;month++)rows.push({YearMonth:`${year}-${String(month).padStart(2,'0')}`,Region:'West',Revenue:year===2023?100:year===2024?200:400,GrossProfit:year===2023?20:year===2024?50:120,Orders:10});
test('cross-year period shifts every month exactly one year',()=>{const p=reportingPeriod(rows,'2024-11','2025-02','West');assert.equal(p.current.Revenue,1200);assert.equal(p.prior.Revenue,600);assert.equal(p.changes.Revenue,100);assert.equal(p.covered,4)});
test('reversed dates are invalid, not zero revenue',()=>assert.throws(()=>reportingPeriod(rows,'2025-12','2025-01'),RangeError));
test('partial history is not a valid YoY',()=>{const p=reportingPeriod(rows,'2023-01','2025-12');assert.equal(p.changes.Revenue,null);assert.equal(p.covered,24)});
test('missing region observations are not comparable',()=>assert.equal(reportingPeriod(rows,'2025-01','2025-12','East').changes.Revenue,null));
test('zero prior revenue is not infinite growth',()=>{const copy=rows.map(r=>({...r,Revenue:0}));assert.equal(reportingPeriod(copy,'2025-01','2025-12').changes.Revenue,null);assert.equal(reportingPeriod(copy,'2025-01','2025-12').margin,null)});
