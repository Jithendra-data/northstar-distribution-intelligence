/* Pure reporting-period contract, shared with Node regression tests. */
function reportingPeriod(rows,from,to,region='all'){
 if(!/^\d{4}-\d{2}$/.test(from)||!/^\d{4}-\d{2}$/.test(to)||from>to)throw new RangeError('From must be on or before Through.');
 const months=[];let y=Number(from.slice(0,4)),m=Number(from.slice(5));
 if(m<1||m>12||Number(to.slice(5))<1||Number(to.slice(5))>12)throw new RangeError('Invalid month');
 while(`${y}-${String(m).padStart(2,'0')}`<=to){months.push(`${y}-${String(m).padStart(2,'0')}`);if(++m===13){m=1;y++}}
 const priorMonths=months.map(x=>`${Number(x.slice(0,4))-1}${x.slice(4)}`),map=new Map();
 rows.filter(r=>region==='all'||r.Region===region).forEach(r=>{const x=map.get(r.YearMonth)||{YearMonth:r.YearMonth,Revenue:0,GrossProfit:0,Orders:0};for(const key of ['Revenue','GrossProfit','Orders'])x[key]+=Number(r[key]||0);map.set(r.YearMonth,x)});
 const sum=keys=>keys.reduce((acc,key)=>{for(const k of ['Revenue','GrossProfit','Orders'])acc[k]+=map.get(key)?.[k]||0;return acc},{Revenue:0,GrossProfit:0,Orders:0});
 const current=sum(months),prior=sum(priorMonths),covered=priorMonths.filter(m=>map.has(m)).length,complete=covered===months.length&&months.every(m=>map.has(m));
 const changes={};for(const key of ['Revenue','GrossProfit','Orders'])changes[key]=complete&&prior[key]!==0?(current[key]-prior[key])/Math.abs(prior[key])*100:null;
 const margin=current.Revenue?current.GrossProfit/current.Revenue*100:null,priorMargin=prior.Revenue?prior.GrossProfit/prior.Revenue*100:null;
 changes.margin=complete&&margin!==null&&priorMargin!==null?margin-priorMargin:null;
 return {current,prior,changes,margin,covered,expected:months.length,complete,priorFrom:priorMonths[0],priorTo:priorMonths.at(-1),trend:months.filter(m=>map.has(m)).map(m=>map.get(m))};
}
if(typeof module!=='undefined')module.exports={reportingPeriod};
