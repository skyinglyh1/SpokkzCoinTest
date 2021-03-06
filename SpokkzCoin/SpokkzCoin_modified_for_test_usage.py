from boa.interop.System.Runtime import *
from boa.interop.System.Storage import *
from boa.builtins import *
from boa.interop.System.Runtime import CheckWitness


# from libs.SafeMath import *
"""
SafeMath
"""
def uSub(a, b):
    """
    Operates a minus b with condition that a - b can never be below 0.
    :param a: operand a
    :param b: operand b
    :return: a - b if a - b > 0 or revert the transaction.
    """
    Require(a >= b)
    return a - b



# from libs.SafeCheck import *
"""
SafeCheck
"""
def Require(condition):
    """
    If not satisfying the condition, revert the transaction. All
    changed storage will be rolled back.
    :param condition: required condition.
    :return: True if satisfying the condition.
    """
    if not condition:
        _ = Revert()
    return True


def RequireScriptHash(key):
    """
    Checks the bytearray parameter is script hash or not. Script Hash
    length should be equal to 20.
    :param key: bytearray parameter to check script hash format.
    :return: True if script hash or revert the transaction.
    """
    _ = Require(len(key) == 20)
    return True


def RequireWitness(witness):
    """
    Checks the transaction sender is equal to the witness. If not
    satisfying, revert the transaction.
    :param witness: required transaction sender
    :return: True if transaction sender or revert the transaction.
    """
    is_witness = CheckWitness(witness)
    _ = Require(is_witness)
    return True


# from libs.Utils import *
"""
Utils
"""
def Revert():
    """
    Revert the transaction by raising an exception.
    """
    raise Exception(0x00)
    # return False


def SafePut(context, key, value):
    if value == 0:
        Delete(context, key)
    else:
        Put(context, key, value)
    return True


TOKEN_NAME = 'Spokkz Token'
TOKEN_SYMBOL = 'SPKZ'

################################################################################
# TOKEN INFO CONSTANTS

DEPLOYER = ToScriptHash('AQf4Mzu1YJrhz9f3aRkkwSm9n3qhXGSh4p')
INIT_SUPPLY = 1000000000
TOKEN_DECIMALS = 8
FACTOR = 100000000

################################################################################
# STORAGE KEY CONSTANT
# Belows are storage key for some variable token information.

OWNER_KEY = '___OWNER'
SPKZ_SUPPLY_KEY = '__SUPPLY'


################################################################################
# STORAGE KEY PREFIX
# Since all data are stored in the key-value storage, the data need to be
# classified by key prefix. All key prefixes length must be the same.

OWN_PREFIX = '_____own'
ALLOWANCE_PREFIX = '___allow'


################################################################################
#

def Main(operation, args):
    # Notify(["111_main", operation, args])
    if operation == 'Deploy':
        ret = Deploy()
        return ret
    if operation == 'name':
        return TOKEN_NAME
    if operation == 'decimals':
        return TOKEN_DECIMALS
    if operation == 'symbol':
        return TOKEN_SYMBOL
    if operation == 'TotalSupply':
        ret = TotalSupply()
        return ret
    if operation == 'BalanceOf':
        if len(args) == 1:
            ret = BalanceOf(args[0])
            return ret
        return False
    if operation == 'Transfer':
        if len(args) == 3:
            ret = Transfer(args[0], args[1], args[2])
            return ret
        return False
    if operation == 'TransferMulti':
        ret = TransferMulti(args)
        return ret
    if operation == 'TransferFrom':
        if len(args) == 4:
            ret = TransferFrom(args[0], args[1], args[2], args[3])
            return ret
        return False
    if operation == 'Approve':
        if len(args) == 3:
            ret = Approve(args[0], args[1], args[2])
            return ret
        return False
    if operation == 'Allowance':
        if len(args) == 2:
            ret = Allowance(args[0], args[1])
            return ret
        return False
    if operation == 'Burn':
        if len(args) == 1:
            ret = Burn(args[0])
            return ret
        return False
    if operation == 'TransferOwnership':
        if len(args) == 1:
            ret = TransferOwnership(args[0])
            return ret
        return False
    return False


def Deploy():
    """
    Constructor of this contract. Only deployer hard-coded can call this function
    and cannot call this function after called once.
    Followings are initialization list for this token
    1. Transfer the owner to the deployer. (Owner can burn the token)
    2. Supply initial coin to the deployer.
    """
    ctx = GetContext()

    is_witness = CheckWitness(DEPLOYER)
    is_deployed = Get(ctx, 'DEPLOYED')
    _ = Require(is_witness)                     # only can be initialized by deployer
    _ = Require(not is_deployed)                # only can deploy once

    # disable to deploy again
    Put(ctx, 'DEPLOYED', 1)

    # the first owner is the deployer
    # can transfer ownership to other by calling `TransferOwner` function
    Put(ctx, OWNER_KEY, DEPLOYER)

    # supply the coin. All coin will be belong to deployer.
    total = INIT_SUPPLY * FACTOR
    Put(ctx, SPKZ_SUPPLY_KEY, total)
    deployer_key = concat(OWN_PREFIX, DEPLOYER)
    Put(ctx, deployer_key, total)
    Notify(['transfer', '', DEPLOYER, total])
    return True


def TotalSupply():
    """
    Gets the total supply for SPKZ token. The total supply can be changed by
    owner's invoking function calls for burning.
    """
    return _totalSupply(GetContext())


def BalanceOf(account):
    """
    Gets the SPKZ token balance of an account.
    :param account: account
    """
    ctx = GetContext()
    balance = _balanceOf(ctx, account)
    return balance


def Transfer(_from, _to, _value):
    """
    Sends the amount of tokens from address `from` to address `to`. The parameter
    `from` must be the invoker.
    :param _from: invoker address.
    :param _to: receiver address.
    :param _value: SPKZ amount.
    """
    _ = RequireWitness(_from)           # from address validation
    ctx = GetContext()
    _ = _transfer(ctx, _from, _to, _value)
    Notify(['transfer', _from, _to, _value])
    return True


def TransferMulti(args):
    """
    Sends tokens to the several people.
    :param args: transfer arguments array
    """
    for p in (args):
        arg_len = len(p)
        _ = Require(arg_len == 3)
        _ = Transfer(p[0], p[1], p[2])
    return True


def TransferFrom(_originator, _from, _to, _amount):
    """
    Transfers the amount of tokens in `from` address to `to` address by invoker.
    Only approved amount can be sent.
    :param _originator: invoker address.
    :param _from: address for withdrawing.
    :param _to: address to receive.
    :param _amount: SPKZ amount.
    """
    ctx = GetContext()
    _ = _transferFrom(ctx, _originator, _from, _to, _amount)
    Notify(['transfer', _from, _to, _amount])
    return True


def Approve(_from, _to, _amount):
    """
    Approves `to` address to withdraw SPKZ token from the invoker's address. It
    overwrites the previous approval value.
    :param _from: invoker address.
    :param _to: address to approve.
    :param _amount: SPKZ amount to approve.
    """
    _ = RequireWitness(_from)       # only the token owner can approve
    ctx = GetContext()
    _ = _approve(ctx, _from, _to, _amount)
    Notify(['approve', _from, _to, _amount])
    return True


def Burn(_amount):
    """
    Burns the amount of SPKZ token from the owner's address.
    :param _amount: SPKZ amount to burn.
    """
    ctx = GetContext()
    _ = _onlyOwner(ctx)                             # only owner can burn the token
    owner_key = Get(ctx, OWNER_KEY)
    burned = _burn(ctx, owner_key, _amount)
    return burned

def TransferOwnership(_account):
    """
    Transfers the ownership of this contract to other.
    :param _account: address to transfer ownership.
    """
    ctx = GetContext()
    _onlyOwner(ctx)
    transferred = _transferOwnership(ctx, _account)
    return transferred


def Allowance(_from, _to):
    """
    Gets the amount of allowance from address `from` to address `to`.
    :param _from: from address
    :param _to: to address
    :return: the amount of allowance.
    """
    ctx = GetContext()
    allowance = _allowance(ctx, _from, _to)
    return allowance


################################################################################
# INTERNAL FUNCTIONS
# Internal functions checks parameter and storage result validation but these
# wouldn't check the witness validation, so caller function must check the
# witness if necessary.

def _transfer(_context, _from, _to, _value):
    _ = Require(_value > 0)             # transfer value must be over 0
    _ = RequireScriptHash(_to)          # to-address validation

    from_val = _accountValue(_context, _from)
    to_val = _accountValue(_context, _to)

    from_val = uSub(from_val, _value)
    to_val = to_val + _value

    from_key = concat(OWN_PREFIX, _from)
    to_key = concat(OWN_PREFIX, _to)
    _ = SafePut(_context, from_key, from_val)
    _ = SafePut(_context, to_key, to_val)

    return True


def _balanceOf(_context, _account):
    _ = RequireScriptHash(_account)
    account_key = concat(OWN_PREFIX, _account)
    balance = Get(_context, account_key)
    return balance


def _transferFrom(_context, _originator, _from, _to, _amount):
    _ = RequireWitness(_originator)
    _ = RequireScriptHash(_from)
    _ = RequireScriptHash(_to)

    _ = Require(_amount > 0)

    from_to_key = concat(_from, _originator)
    approve_key = concat(ALLOWANCE_PREFIX, from_to_key)
    approve_amount = Get(_context, approve_key)
    approve_amount = uSub(approve_amount, _amount)

    _ = _transfer(_context, _from, _to, _amount)
    _ = SafePut(_context, approve_key, approve_amount)

    return True


def _approve(_context, _from, _to, _amount):
    _ = RequireScriptHash(_to)          # to-address validation
    _ = Require(_amount >= 0)           # amount must be not minus value
    from_val = _accountValue(_context, _from)

    _ = Require(from_val >= _amount)    # the token owner must have the amount over approved
    from_to_key = concat(_from, _to)
    approve_key = concat(ALLOWANCE_PREFIX, from_to_key)
    SafePut(_context, approve_key, _amount)
    return True


def _burn(_context, _account, _amount):
    _ = Require(_amount > 0)                # the amount to burn should be over 0

    account_val = _balanceOf(_context, _account)
    total_supply = _totalSupply(_context)

    _ = Require(_amount < total_supply)     # should be not over total supply

    # burn the token from account. It also subtract the total supply
    account_val = uSub(account_val, _amount)
    total_supply = uSub(total_supply, _amount)

    account_key = concat(OWN_PREFIX, _account)
    _ = SafePut(_context, account_key, account_val)
    _ = SafePut(_context, SPKZ_SUPPLY_KEY, total_supply)
    return True


def _transferOwnership(_context, _account):
    _ = RequireScriptHash(_account)
    Put(_context, OWNER_KEY, _account)
    return True


################################################################################
# modifiers

def _onlyOwner(_context):
    """
    Checks the invoker is the contract owner or not. Owner key is saved in the
    storage key `___OWNER`, so check its value and invoker.
    """
    owner = Get(_context, OWNER_KEY)
    _ = RequireWitness(owner)
    return True


################################################################################
#

def _accountValue(_context, _account):
    account_key = concat(OWN_PREFIX, _account)
    account_balance = Get(_context, account_key)
    return account_balance


def _totalSupply(_context):
    total_supply = Get(_context, SPKZ_SUPPLY_KEY)
    return total_supply


def _allowance(_context, _from, _to):
    from_to_key = concat(_from, _to)
    allowance_key = concat(ALLOWANCE_PREFIX, from_to_key)
    allowance = Get(_context, allowance_key)
    return allowance
