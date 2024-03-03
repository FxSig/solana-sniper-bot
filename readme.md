## 简介
```commandline

(en)
solana raydium new pool detector

(zh)
solana 新池探测机器人
```

### 环境安装
```commandline
pip install -r requirements.txt
```

### 配置解释
```commandline
private_key     私钥
is_buy          是否自动买入(自动买入(1)    不买入(0))
is_sell         是否自动卖出(自动卖出(1)    不卖出(0))
pool_size       资金池大于多少时买入
sol_amount      买入金额(以solana为单位)
wait_seconds    多长时间后卖出
```