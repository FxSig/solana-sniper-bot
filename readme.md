<div align="center">
    <h1>📟 SOLANA SNIPER BOT IN PYTHON 🪐</h1>
<img src="https://github.com/DevSolana/solana-sniper-python/assets/163946998/ed2bac1b-0bf6-4a84-b813-431902fcba2b">


</div>

---

<p align="center">
    <img src="https://img.shields.io/github/stars/DevSolana/solana-sniper-python">
    <img src="https://img.shields.io/github/forks/DevSolana/solana-sniper-python">
    <br>
    <img src="https://img.shields.io/github/issues/DevSolana/solana-sniper-python">
    <img src="https://img.shields.io/github/issues-closed/DevSolana/solana-sniper-python">
    <br>
    <img src="https://img.shields.io/github/languages/top/DevSolana/solana-sniper-python">
    <img src="https://img.shields.io/github/last-commit/DevSolana/solana-sniper-python">
    <br>
</p>

# ✨ Quickstart

This code is written as proof of concept to demonstrate how we can buy new tokens immediately after the liquidity pool is open for trading.

Script listens to new Raydium USDC or SOL pools and buys tokens for a fixed amount in USDC/SOL.
Depending on the speed of the RPC node, the purchase usually happens before the token is available on Raydium UI for swapping.

This is provided as is, for learning purposes.

## 🛠️ Installation

💾 **Clone this repository**
```sh
git clone https://github.com/DevSolana/solana-sniper-python
```

💻 **Install dependences**
```sh
pip3 install -r requirements.txt
```

▶️ **Start CLI**
```sh
python main.py
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

# 🗨️ Q&A
### Where are my private keys?
*Your private keys are stored in `config.ini`.*
### Is there any fees when swapping using CLI?
*There are no additional fees when performing swaps via the CLI; the costs should be the same as using the Jupiter UI.*
### Does sniper bot remains running if I close the CLI?
*If you close the CLI, the sniper bot will stop running.*
### Is it possible to swap any tokens?
*You can only swap tokens that are listed on Jupiter based on their criterias.*

# 🚨 Known bugs

# 📝 TO-DO
- [ ] Clean up code ⚡


# 🤝 Contributions
If you are interesting in contributing, fork the repository and submit a pull request in order to merge your improvements into the main repository.<br>
Contact me for any inquiry, I will reach you as soon as possible.<br>

# 👑 Donations
This project doesn't include platform fees. If you find value in it and would like to support its development, your donations are greatly appreciated.<br>
You can donate through CLI in About menu.<br>
**SOLANA ADDRESS**
```sh
FHzUJaDEhqSxfM39p4WCqE5WP9HMwGADqdjNHs3mcGWo
```

