# Note: this contract is only for testing

contract EthFlash():
    def flash(amount: uint256(wei), deadline: timestamp): modifying
    def returnLoan(): modifying

malicious: bool

@public
@payable
def __init__(_malicious: bool):
    self.malicious = _malicious

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
def flash_loan_eth(eth_flash: address, amount: uint256(wei), deadline: timestamp):
    EthFlash(eth_flash).flash(amount, deadline)