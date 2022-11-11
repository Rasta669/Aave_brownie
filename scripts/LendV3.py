from re import A
from brownie import interface, config, network
from scripts.helpful_scripts import (
    LOCAL_DEVELOPMENT_NETWORKS,
    get_account,
    approve_erc20,
)
from scripts.get_weth import get_weth
from web3 import Web3

gasPrice = Web3.toWei(0.1, "gwei")

AMOUNT = Web3.toWei(0.05, "ether")


def lend_and_borrow():
    if network.show_active() in LOCAL_DEVELOPMENT_NETWORKS:
        account = get_weth()
    else:
        account = get_account()
    APPR_address = config["networks"][network.show_active()][
        "lending_pool_addresses_provider_registry"
    ]
    APPR = interface.IPoolAddressesProviderRegistry(APPR_address)
    list = APPR.getAddressesProvidersList()
    id = APPR.getAddressesProviderIdByAddress(
        "0xc4dCB5126a3AfEd129BC3668Ea19285A9f56D15D"
    )
    APP = interface.IPoolAddressesProvider("0xc4dCB5126a3AfEd129BC3668Ea19285A9f56D15D")
    a_pool_address = APP.getPool()
    aave_oracle_address = APP.getPriceOracle()
    print(list, id, a_pool_address, aave_oracle_address, APP.getAddress(30))
    a_pool = interface.IPool(a_pool_address)
    # approving weth asset
    weth_asset = config["networks"][network.show_active()]["weth_token"]
    approve_erc20(weth_asset, a_pool, AMOUNT, account)
    # supplying weth
    print("Supplying Weth")
    supply_tx = a_pool.supply(weth_asset, AMOUNT, account, 0, {"from": account})
    supply_tx.wait(1)
    print("Successfully supplied weth to aave...")
    # get configuration data
    (
        totalCollateralBase,
        totalDebtBase,
        availableBorrowsBase,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = a_pool.getUserAccountData(account)
    print(
        totalCollateralBase,
        totalDebtBase,
        availableBorrowsBase,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    )
    # read_data
    read_aave_data(account, a_pool)
    # get equivalent usdc borrow amount in relation to amount supplied
    borrow_asset = config["networks"][network.show_active()]["usdc_contract"]
    aave_oracle = interface.IAaveOracle(aave_oracle_address)
    borrow_asset_price = aave_oracle.getAssetPrice(borrow_asset)
    borrow_amount = availableBorrowsBase * 0.3 / 10**2
    # borrowing assets (usdc)
    print("Borrowing...")
    borrow_tx = a_pool.borrow(
        borrow_asset,
        borrow_amount,
        1,
        0,
        account,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("borrowed...")
    read_aave_data(account, a_pool)
    return account, a_pool, borrow_asset, borrow_amount


def repay(account, a_pool, borrow_asset, amount):
    account = account
    print("repaying...")
    repay_tx = a_pool.repay(borrow_asset, amount, 1, account, {"from": account})
    repay_tx.wait(1)
    print("repayed....")
    read_aave_data(account, a_pool)


def repay_with_Atokens(account, a_pool, borrow_asset, amount):
    account = account
    print("repaying with your a tokens")
    repay_tx = a_pool.repayWithATokens(borrow_asset, amount, 1, {"from": account})
    repay_tx.wait(1)


def approve_erc20(asset, spender, amount, account=None):
    if account:
        account = account
    else:
        account = get_account()
    print("approving asset")
    tx = interface.IERC20(asset).approve(spender, amount, {"from": account})
    tx.wait(1)
    print("asset approved")


def read_aave_data(account, a_pool):
    account = account
    (
        totalCollateralBase,
        totalDebtBase,
        availableBorrowsBase,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = a_pool.getUserAccountData(account)
    print(
        totalCollateralBase,
        totalDebtBase,
        availableBorrowsBase,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    )


def withdraw_assets(account, pool, amount, asset):
    account = account
    print("withdrawing funds")
    withdraw_tx = pool.withdraw(asset, amount, account, {"from": account})
    withdraw_tx.wait(1)


def main():
    # (account, pool, borrow_asset, borrow_amount) = lend_and_borrow()
    account = get_account()
    APP = interface.IPoolAddressesProvider("0xc4dCB5126a3AfEd129BC3668Ea19285A9f56D15D")
    a_pool_address = APP.getPool()
    pool = interface.IPool(a_pool_address)
    read_aave_data(account, pool)
    borrow_asset = borrow_asset = config["networks"][network.show_active()][
        "usdc_contract"
    ]
    (
        totalCollateralBase,
        totalDebtBase,
        availableBorrowsBase,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = pool.getUserAccountData(account)
    borrow_amount = totalDebtBase / (10**2)
    # repay(account, pool, borrow_asset, borrow_amount)
    repay_with_Atokens(account, pool, borrow_asset, borrow_amount)
