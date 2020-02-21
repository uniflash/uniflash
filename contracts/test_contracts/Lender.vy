# Note: this contract is only for testing
from vyper.interfaces import ERC20

contract EthFlash():
    def flash(amount: uint256(wei), deadline: timestamp): modifying
    def returnLoan(): modifying

contract ERC20Flash():
    def flash(amount: uint256, deadline: timestamp): modifying

malicious: bool
token: address

@public
def __init__(_malicious: bool, _token: address):
    self.malicious = _malicious
    self.token = _token

@public
@payable
def __default__():
    pass

@public
def ethDeFi(loan: uint256(wei), interest: uint256(wei)):
    to_return: uint256(wei) = loan + interest
    assert self.balance >= to_return
    if (not self.malicious):
        EthFlash(msg.sender).returnLoan(value=to_return)

@public
def erc20DeFi(loan: uint256, interest: uint256):
    to_return: uint256 = loan + interest
    assert ERC20(self.token).balanceOf(self) >= to_return
    if (not self.malicious):
        ERC20(self.token).transfer(msg.sender, to_return)

@public
def flash_loan_eth(eth_flash: address, amount: uint256(wei), deadline: timestamp):
    EthFlash(eth_flash).flash(amount, deadline)

@public
def flash_loan_erc20(erc20_flash: address, amount: uint256, deadline: timestamp):
    ERC20Flash(erc20_flash).flash(amount, deadline)