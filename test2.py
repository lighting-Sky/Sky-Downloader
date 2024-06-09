import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE',
    'Cookie':"ZMRhjlxmTSDeenable=true; ZMRhjlxmTSDe443S=8x1a.kxRExAE8kc.fIImO7s_6NRkoGIa2av1IDA075cktCvoAbjR4UQ.sHsQdhNX; _pk_ref.15.55be=%5B%22%22%2C%22%22%2C1717514449%2C%22https%3A%2F%2Fcn.bing.com%2F%22%5D; _pk_ses.15.55be=1; _pk_ses.71.55be=1; _pk_id.15.55be=7965dd34222c9813.1717514449.1.1717515892.1717514449.; ZMRhjlxmTSDe443T=5DjM9pGDMZFDWu1qlKRkLP0ADDNM6FUgnZjXzUSLE0F2BacZ5qnTaIiUzeuqZSWXS.xnlQoR7fT4hPKVu8noYIvq236Cke_P8Gc3WWLCHCB6g5nMD5SBLisbhX0_cBsAzy.ozxJ_KeItCZDjhIT_0UpXXl3X679EkcbpFxIM.Zzjv90fQZCV_WyY_sbySFcQkE.SDgG8fnga7ShpSmdvL1dZK1PIus5DMSb2b0PY2vXYZBewnMMB_IpsSH7axL6qFeX1iEbnwqBi9tvajqoyfQjQ9cxaJvZKIvKsexVFxhU94kcFa_NfR.N7hBFIPPZh_ln07nhD8A1azmFuj0_ljE3tP; _pk_id.71.55be=c84e01980e9affef.1717514452.1.1717516437.1717514452."
}
url = "https://graduate.sysu.edu.cn/zsw/"
response = requests.get(url=url, headers=headers)
with open("index.html", "wb") as f:
    f.write(response.content)