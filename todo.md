### Required
- [X] Build an RSA encoder/decoder
  * Cut the msg into pices when it's larger than the `n`, \
  not the recommended way, but that what was required
- [X] Build a tcp server
- [X] Build a tcp client
  * can choose to use pre-computed using `-c <config.json:file>`
  * can choose the number of bits to be used for keys using `-b <bits:decimal_int>`
- [X] Do rsa attacks 
  * Bruteforce attack on `n`
  * Chosen Cipher Text attack
      
### Test Mode
- [X] (p, q, e, d)
- [ ] (p, q, e)
- [ ] (p, q, d)
- [ ] (n, e)
- [ ] (n, d)
- [ ] (n, phi)
- [X] check the relative math correctness conditions

### Advanced
- [X] Add logs to the server
- [ ] Ensure verfication, intigrity with the enc/dec method
- [ ] Add Different Encryption/Decryption Modes like this hybrid one: \
    key=aes256-gcm.genkey() -> aes256-gcm.enc(msg, key) -> enc_key=rsa.enc(key) \
    then send(msg || iv || enc_key)
- [ ] Add colors to the terminal
- [ ] May be adding a simple sqlite3 db
- [ ] Change the key with every message

### Cleaning the code
- [X] Fix server/client issues i.e. encode/decode str/bytes
- [X] Fix the `broken pipe - errorno 32` issue
- [ ] Make `e` of the key be dynamic not static
- [ ] Map the avaliable commands to a coressopnding functions like: \
    {"/list": list_users, "/bad": "log_received_bad_msg", "/quit": shutdown_client, ...}
- [ ] Fix the real-time message receiving issue in cases like
  - [ ] When talking to a certain client
  - [ ] When not engaging in any converstaion
