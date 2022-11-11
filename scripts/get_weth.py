from brownie import interface, config, network
from scripts.helpful_scripts import get_account


def main():
    get_weth()


##this scripts deposits weth to your account in exchange for eth
def get_weth():
    account = get_account()
    weth = interface.WethInterface(
        config["networks"][network.show_active()]["weth_token"]
    )
    print("depositing eth!")
    tx = weth.deposit({"from": account, "value": 0.2 * 10**18})
    tx.wait(1)
    balanceWeth = weth.balanceOf(account)
    print(f"Your Weth balance is {balanceWeth}")
    return account
