"""Fail-closed publication policy; only synthetic negative stock has an exception."""
import math

def enforce_controls(results, *, synthetic=True):
    if not results: raise ValueError('No quality controls supplied')
    for row in results:
        expected = synthetic and row['TestName'] == 'Negative ending on-hand'
        row['Severity'] = 'EXPECTED_SCENARIO' if expected else 'BLOCKING'
        row['ExceptionReason'] = 'Generated stock-shortage scenario; not accepted for real ERP data.' if expected else ''
    blocked=[r['TestName'] for r in results if r['Status']!='PASS' and r['Severity']=='BLOCKING']
    if blocked: raise ValueError('Publication blocked: '+', '.join(blocked))

def validate_contract(payload):
    required={'revenue','gross_profit','gross_margin','units','orders','customers','inventory_value','open_po_value'}
    k=payload.get('executive_kpis',{})
    if not required.issubset(k): raise ValueError('Incomplete KPI contract')
    if any(not isinstance(k[x],(float,int)) or not math.isfinite(k[x]) for x in required): raise ValueError('Nonfinite KPI contract')
    if not payload.get('sales_trend_by_region'): raise ValueError('Missing monthly reporting coverage')
    for field,key in [('Revenue','revenue'),('GrossProfit','gross_profit'),('Units','units')]:
        if abs(sum(float(r[field]) for r in payload.get('sales_trend',[]))-k[key])>0.01: raise ValueError('Monthly totals do not match KPI: '+key)
    for field,key in [('Revenue','revenue'),('GrossProfit','gross_profit'),('Orders','orders')]:
        if abs(sum(float(r[field]) for r in payload['sales_trend_by_region'])-k[key])>0.01: raise ValueError('Regional totals do not match KPI: '+key)
    if k['revenue'] and abs(k['gross_profit']/k['revenue']-k['gross_margin'])>0.000001: raise ValueError('Margin contract inconsistent')
    rec=payload.get('reconciliation',[])
    if {r['Measure'] for r in rec}!={'Revenue','GrossProfit','Units','EndingInventoryValue','OpenPOValue'}: raise ValueError('Incomplete reconciliation')
    if any(r['Status']!='PASS' for r in rec): raise ValueError('Reconciliation blocked publication')
    measures={'Revenue':'revenue','GrossProfit':'gross_profit','Units':'units','EndingInventoryValue':'inventory_value','OpenPOValue':'open_po_value'}
    for r in rec:
        tolerance=0.000001 if r['Measure']=='Units' else 0.01
        values=[r.get(key) for key in ['RawValue','FactValue','DashboardValue']]
        if any(not isinstance(v,(int,float)) or not math.isfinite(v) for v in values): raise ValueError('Missing independent totals')
        if max(abs(values[0]-values[1]),abs(values[0]-values[2]),abs(values[2]-k[measures[r['Measure']]]))>tolerance: raise ValueError('Invalid reconciliation values')
    enforce_controls(payload.get('data_quality',{}).get('results',[]),synthetic=payload.get('pipeline_metadata',{}).get('dataset_type')=='synthetic')

def main():
    import json
    from pathlib import Path
    payload=json.loads(Path('web/data/dashboard.json').read_text(encoding='utf-8'))
    validate_contract(payload)
    if payload.get('pipeline_metadata',{}).get('publication_status')!='APPROVED': raise ValueError('Dataset has no approval manifest')
    print('Published contract and gate evidence verified')

if __name__=='__main__': main()
