![image](https://github.com/DevSolana/solana_swap_sniper/assets/163946998/7cf4a361-1ba1-4d9d-a200-9c4854130090)

### Introduction
```commandline

(en)
solana raydium new pool detector

(zh)
solana 新池探测机器人
```

### Environment installation

```commandline
pip install -r requirements.txt
python3 main.py
```

### Configuration explanation
```commandline
private_key     private key
is_buy          Whether to buy automatically (buy automatically (1) or not (0))
is_sell         Whether to sell automatically (sell automatically (1) or not (0))
pool_size       Buy when the capital pool is larger than
sol_amount      Buying amount (in solana)
wait_seconds    How long to sell after (in ms)
```
