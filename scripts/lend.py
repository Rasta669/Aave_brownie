from brownie import interface, network, config
from scripts.helpful_scripts import get_account, approve_erc20
from scripts.get_weth import get_weth
from web3 import Web3

mainnetFork = ["mainnet-fork-dev"]


def main():
    deposit_borrow_weth()
    ##get_lending_pool()


Amount = 100000000000000000


def deposit_borrow_weth():
    account = get_account()
    weth_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in mainnetFork:
        get_weth()
    ##locating the lending pooladdress
    lendingPoolAddress = get_lending_pool()
    ##approving the lending pool to spend the weth on our behalf
    approve_erc20(weth_address, lendingPoolAddress, Amount, account)
    ##abi, address of lending pool contract
    lending_pool = interface.ILendingPool(lendingPoolAddress)
    ##depositing
    print("depositing!!!")
    tx = lending_pool.deposit(weth_address, Amount, account, 0, {"from": account})
    tx.wait(1)
    print("Yeay deposited some Weth!!")
    ##getting the account info
    (
        totalCollateralETH,
        totalDebtETH,
        availableBorrowsETH,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = lending_pool.getUserAccountData(account)

    print(f"You have {Web3.fromWei(totalCollateralETH, 'ether')}ETH deposited!!")
    print(f"You have {Web3.fromWei(totalDebtETH, 'ether')}ETH in debt!!")
    print(
        f"You have {Web3.fromWei(availableBorrowsETH, 'ether')}ETH available to borrow..."
    )
    print(f"Your current liquidation threshold is {currentLiquidationThreshold} >>>")
    ##getting asset price
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    print(f"The price of Dai is {Web3.fromWei(dai_eth_price, 'ether')}ETH")
    ##borrowing (borrowable_amount in dai)
    borrowable_amount = (availableBorrowsETH * 0.9) * 10**18 / dai_eth_price
    dai_asset = config["networks"][network.show_active()]["dai_contract"]
    print("Borrowing....")
    tx = lending_pool.borrow(
        dai_asset, borrowable_amount, 1, 0, account, {"from": account}
    )
    tx.wait(1)
    print(f"Borrowed Some Dai!!")
    ##getting updated data
    (
        totalCollateralETH2,
        totalDebtETH2,
        availableBorrowsETH2,
        currentLiquidationThreshold2,
        ltv2,
        healthFactor2,
    ) = lending_pool.getUserAccountData(account)

    print(f"You have {Web3.fromWei(totalCollateralETH2, 'ether')}ETH deposited!!")
    print(f"You have {Web3.fromWei(totalDebtETH2, 'ether')}ETH in debt!!")
    print(
        f"You have {Web3.fromWei(availableBorrowsETH2, 'ether')}ETH available to borrow..."
    )
    print(f"Your current liquidation threshold is {currentLiquidationThreshold2} >>>")
    ##repaying
    ##repay_all(borrowable_amount, lending_pool, dai_asset, account, 1)
    ##getting updated data
    (
        totalCollateralETH3,
        totalDebtETH3,
        availableBorrowsETH3,
        currentLiquidationThreshold3,
        ltv3,
        healthFactor3,
    ) = lending_pool.getUserAccountData(account)

    print(f"You have {Web3.fromWei(totalCollateralETH3, 'ether')}ETH deposited!!")
    print(f"You have {Web3.fromWei(totalDebtETH3, 'ether')}ETH in debt!!")
    print(
        f"You have {Web3.fromWei(availableBorrowsETH3, 'ether')}ETH available to borrow..."
    )
    print(f"Your current liquidation threshold is {currentLiquidationThreshold3} >>>")


def repay_all(amount, lending_pool, asset, account, rateMode):
    ##approve erc2o
    print("Approving for repaying...")
    approve_erc20(asset, lending_pool, amount, account)
    ##repaying
    print("Repaying...")
    lending_pool.repay(asset, amount, rateMode, account, {"from": account})
    print("Yeeay repaid....")


def get_asset_price(price_feed_contract):
    ##abi, address of the price feed contract
    asset_price = interface.AggregatorV3Interface(price_feed_contract)
    Asset_price = asset_price.latestRoundData()[1]
    return Asset_price


def get_lending_pool():
    lending_pool_address_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool = lending_pool_address_provider.getLendingPool()
    ##print(lending_pool)
    return lending_pool
