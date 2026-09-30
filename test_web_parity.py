"""Compare browser BigInt results against the unchanged Python MCP core."""
import json, random, subprocess, unittest
from pathlib import Path
from calculator import calculate_discount_range

class WebParity(unittest.TestCase):
    def test_parity(self):
        rng = random.Random(42)
        cases = []
        for d, n in [(3, 1), (1000, 999), (1000000, 999999), (100, 0), (100, 100), (10**15, 1)]:
            cases.append([dict(name='商品', original=str(d), sale=str(n))])
        for _ in range(100):
            rows=[]
            for i in range(rng.randint(1, 10)):
                d=rng.randint(1, 10**10); n=rng.randint(0,d)
                rows.append(dict(name=f'商品{i}',original=f'{d//1000000}.{d%1000000:06}',sale=f'{n//1000000}.{n%1000000:06}'))
            cases.append(rows)
        script="""import {calculate} from './docs/calculator.mjs';
let input='';for await(const chunk of process.stdin)input+=chunk;
console.log(JSON.stringify(JSON.parse(input).map(rows=>{const r=calculate(rows,'會員限定');return {low:r.low.zhe,high:r.high.zhe,min:r.high.off,max:r.low.off,copies:r.copies};})));"""
        result=subprocess.run(['node','--input-type=module','-e',script],input=json.dumps(cases),text=True,capture_output=True,cwd=Path(__file__).parent,check=True)
        for case,web in zip(cases,json.loads(result.stdout)):
            p=calculate_discount_range([dict(id=str(i),name=r['name'],original_price=r['original'],sale_price=r['sale']) for i,r in enumerate(case)],conditions='會員限定')
            s=p['summary']
            self.assertEqual(web,dict(low=s['lowest_zhe'],high=s['highest_zhe'],min=s['minimum_percent_off'],max=s['maximum_percent_off'],copies=p['suggested_copy']))

if __name__=='__main__':unittest.main()
