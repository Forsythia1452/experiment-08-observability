import argparse,time,requests
from concurrent.futures import ThreadPoolExecutor

p=argparse.ArgumentParser();p.add_argument('--base',default='http://127.0.0.1:8008');p.add_argument('--count',type=int,default=60);p.add_argument('--concurrency',type=int,default=4);p.add_argument('--delay-ms',type=int,default=150);p.add_argument('--fail-every',type=int,default=10);a=p.parse_args()
if not (0<=a.delay_ms<=2000 and 1<=a.count<=500 and 1<=a.concurrency<=20):raise SystemExit('参数超出本地安全限制')
start=time.time()
def one(i):
    r=requests.get(f'{a.base}/work/{i}',params={'delay_ms':a.delay_ms,'fail':str(bool(a.fail_every and i%a.fail_every==0)).lower()},timeout=5);return r.status_code
with ThreadPoolExecutor(max_workers=a.concurrency) as pool: codes=list(pool.map(one,range(a.count)))
print({'start':start,'end':time.time(),'count':len(codes),'status':{c:codes.count(c) for c in set(codes)}})

