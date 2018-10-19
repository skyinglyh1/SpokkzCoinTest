1. In Revet method from libs.Utils, <code> return False </code> is useless, the program will not go there.
2. We have updated [neo-boa](https://github.com/ontio/neo-boa) such that when the defined function is invoked, we can leave the leftside as empty like <code>Require(2 > 1)</code>. Just make sure you have updated neo-boa in ontio-github.
3. For now, please make sure ```if operation=='init'```, then your method should have the name as ```init()```.
4. You can set ```ctx = GetContext()``` as the global variable and utilize ctx globally and conveniently.
5. ```_ = Require(_amount > 0)``` will always be right unless _amount = 0. So, in you contract, you will not allow Zero transfer, correct?
6. In ```_burn()``` method, if you have 
```_ = Require(_amount < total_supply)     # should be not over total supply```. 
Then you should also have
```_ = Require(_amount < account_val)     # should be not over total supply```
However, you can delete the above code since the following code makes sure that if the above conditions are not satisfied the ```_burn()``` method will raise exception.
```account_val = uSub(account_val, _amount),```
```total_supply = uSub(total_supply, _amount)```
7. You can avoid use ```Get(GetContext(), KEY)``` at several places. For example, in your ```_transfer()``` method, ```from_val = _accountValue(_context, _from)``` needs to form ```concat(OWN_PREFIX, _from)```, yet then you form ```from_key = concat(OWN_PREFIX, _from)``` again. Note the opcode will increase and the invoking gas will increase.
8. Please make sure you test your contract smoothly first. In your ```Main``` function, too many ```elif```, the vm cannot go into ```Approve``` (when doing test here using latest ontology source and neo-boa). However if you set 
```if operation == 'Approve':```, then the contract will be fine. Suggest you all use ```if``` in the main function.
9. In ```Burn()``` method, when you transfer ```amount ``` of tokens to zero address, you should fire the event by using ```Notify```.




















<!-- 6. In ```_approve()``` method, ```approve_key = ALLOWANCE_PREFIX + _from + _to```, where ```_from``` is the owner, ```_to``` is the spender.
1. In ```_transferFrom()``` method, ```approve_key = ALLOWANCE_PREFIX + _from + _originator```, where ```_originator is the spender```, ```_from``` is the owner -->
