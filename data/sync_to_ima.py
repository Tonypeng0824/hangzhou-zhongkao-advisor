#!/usr/bin/env python3
"""Sync strategy_kb.yaml to IMA knowledge base.
Usage: python sync_to_ima.py [--kb-name "杭州中考志愿填报"]
Run automatically after each YAML knowledge base update.
"""

import os, json, requests, hmac, hashlib, time, sys
from datetime import datetime

IMA_BASE = 'https://ima.qq.com'
KB_ID = 'aULvczQ3oF8Y-GVR_z_jRAjGT_hk46xN_GOk3OktWq0='  # 杭州中考
YAML_PATH = os.path.join(os.path.dirname(__file__), 'strategy_kb.yaml')

def get_creds():
    cid_path = os.path.expanduser('~/.config/ima/client_id')
    akey_path = os.path.expanduser('~/.config/ima/api_key')
    if not os.path.exists(cid_path) or not os.path.exists(akey_path):
        print('ERROR: IMA credentials not found. Set up ~/.config/ima/client_id and api_key')
        sys.exit(1)
    return (open(cid_path).read().strip(), open(akey_path).read().strip())

def upload():
    client_id, api_key = get_creds()
    h = {'Content-Type': 'application/json', 
         'ima-openapi-clientid': client_id, 'ima-openapi-apikey': api_key}
    
    if not os.path.exists(YAML_PATH):
        print(f'ERROR: {YAML_PATH} not found')
        sys.exit(1)
    
    with open(YAML_PATH, 'r', encoding='utf-8') as f:
        yaml_content = f.read()
    
    # Count lines and size
    lines = yaml_content.count('\n') + 1
    ts = datetime.now().strftime("%Y%m%d%H%M")
    version = 'v2.6'
    filename = f'strategy_kb_{version}_{ts}.md'
    
    md = f'''# 杭州中考志愿填报知识库 {version}

> 同步: {datetime.now().strftime("%Y-%m-%d %H:%M CST")} | {lines}行 | {len(yaml_content.encode())//1024}KB
> 数据源: 杭州市教育局·潮新闻·杭州网·抖音·19楼·小红书·B站·知乎

## 2026核心参数
- 分配生: 9021人(30招生单位) | 比例: 20.5% | 一段线: 565(2025:563)
- 重高线: 617 | 前三: 628-631 | 前八分配: 3662(70%) | 分校: 5359(40%)

## 一模划线
| 区 | 前三线 | 重高线 | 优高线 |
|----|--------|--------|--------|
| 拱墅 | 588.5 | 574 | 521.5 |
| 西湖 | 584.5 | 570 | 519 |
| 钱塘 | 595.5 | 568估 | 519估 |
| 上城 | 559(A) | - | 515(B) |
| 滨江 | 584 | - | - |

## U1-U5策略更新
基于2025真实案例: 超常警告·冲幅10-20·强制托底·密集段·最低名次x1.35

## YAML数据库
```yaml
{yaml_content[:30000]}
```
*自动同步: WorkBuddy > hangzhou-zhongkao-advisor*
'''
    
    md_bytes = md.encode('utf-8')
    file_size = len(md_bytes)
    print(f'Uploading {filename} ({file_size} bytes) to IMA...')
    
    # Step 1: create_media
    r = requests.post(f'{IMA_BASE}/openapi/wiki/v1/create_media', headers=h, json={
        'file_name': filename, 'file_size': file_size,
        'content_type': 'text/markdown', 'knowledge_base_id': KB_ID, 'file_ext': 'md'
    }, timeout=30)
    cm = r.json()
    if cm.get('code') != 0:
        print(f'FAIL: create_media - {cm.get("msg")}')
        return False
    
    media_id, cred = cm['data']['media_id'], cm['data']['cos_credential']
    
    # Step 2: COS upload
    host = f'{cred["bucket_name"]}.cos.{cred["region"]}.myqcloud.com'
    cos_key = cred['cos_key']
    url = f'https://{host}/{cos_key}'
    
    now = int(time.time())
    kt = f'{now};{now+600}'
    sign_key = hmac.new(cred['secret_key'].encode(), kt.encode(), 'sha1').hexdigest()
    http_str = f"put\n/{cos_key}\n\ncontent-length={file_size}&host={host}\n"
    sha1_http = hashlib.sha1(http_str.encode()).hexdigest()
    sig = hmac.new(sign_key.encode(), f"sha1\n{kt}\n{sha1_http}\n".encode(), 'sha1').hexdigest()
    auth = (f'q-sign-algorithm=sha1&q-ak={cred["secret_id"]}&q-sign-time={kt}'
            f'&q-key-time={kt}&q-header-list=content-length;host'
            f'&q-url-param-list=&q-signature={sig}')
    
    r2 = requests.put(url, data=md_bytes, headers={
        'Content-Type': 'text/markdown', 'Content-Length': str(file_size),
        'Host': host, 'Authorization': auth, 'x-cos-security-token': cred['token']
    }, timeout=60)
    if r2.status_code != 200:
        print(f'FAIL: COS upload - {r2.status_code}')
        return False
    
    # Step 3: add_knowledge
    r3 = requests.post(f'{IMA_BASE}/openapi/wiki/v1/add_knowledge', headers=h, json={
        'knowledge_base_id': KB_ID, 'media_id': media_id, 'title': filename, 'media_type': 7
    }, timeout=30)
    ak = r3.json()
    if ak.get('code') == 0:
        print(f'SUCCESS: {filename} -> IMA知识库 (彭波&Tony)')
        return True
    else:
        print(f'FAIL: add_knowledge - {ak.get("msg")}')
        return False

if __name__ == '__main__':
    upload()
