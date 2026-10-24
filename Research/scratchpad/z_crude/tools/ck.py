import json,sys
null=None; true=True; false=False
rec=eval(sys.stdin.read())
open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gt/ckpt_crude.jsonl','a').write(json.dumps(rec)+'\n'); print('appended',rec['image'])
