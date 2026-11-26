from pathlib import Path
import json

root=Path(__file__).resolve().parents[2]/'Runtime'/'data'/'dbt_runs'
expected={'silver_events':2.441,'silver_ticket_types':3.724,'silver_orders':7.264,
          'silver_order_items':29.972,'silver_payments':19.105,'fact_ticket_sales':6.936}
found=[]
for p in root.glob('*/target/run_results.json'):
    data=json.loads(p.read_text(encoding='utf8'))
    for r in data.get('results',[]):
        model=r.get('unique_id','').split('.')[-1]
        if model in expected and round(r.get('execution_time',0),3)==expected[model]:
            found.append({'model':model,'execution_time':r['execution_time'],
                          'generated_at':data.get('metadata',{}).get('generated_at'),
                          'timing':r.get('timing'), 'path':str(p)})
print(json.dumps(found,ensure_ascii=False,indent=2))
