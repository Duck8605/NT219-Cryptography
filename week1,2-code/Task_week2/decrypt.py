from collections import Counter

# Known English letter frequencies (from most frequent to least frequent)
english_frequencies = 'ETAOINSHRDLCUMWFGYPBVKJXQZ'

cipher_text = "hzsrnqc klyy wqc flo mflwf ol zqdn nsoznj wskn lj xzsrbjnf, wzsxz gqv zqhhnf ol ozn glco zlfnco hnlhrn; nsoznj jnrqosdnc lj fnqj kjsnfbc, wzsxz sc xnjoqsfrv gljn efeceqr. zn rsdnb qrlfn sf zsc zlecn sf cqdsrrn jlw, wzsoznj flfn hnfnojqonb. q csfyrn blgncosx cekksxnb ol cnjdn zsg. zn pjnqmkqconb qfb bsfnb qo ozn xrep, qo zlejc gqozngqosxqrrv ksanb, sf ozn cqgn jllg, qo ozn cqgn oqprn, fndnj oqmsfy zsc gnqrc wsoz loznj gngpnjc, gexz rncc pjsfysfy q yenco wsoz zsg; qfb wnfo zlgn qo naqxorv gsbfsyzo, lfrv ol jnosjn qo lfxn ol pnb. zn fndnj ecnb ozn xlcv xzqgpnjc wzsxz ozn jnkljg hjldsbnc klj soc kqdlejnb gngpnjc. zn hqccnb onf zlejc leo lk ozn ownfov-klej sf cqdsrrn jlw, nsoznj sf crnnhsfy lj gqmsfy zsc olsrno."

# Counting letter frequencies in the ciphertext
cipher_counts = Counter(''.join(filter(str.isalpha, cipher_text)))

# Sorting the dictionary by frequency
sorted_cipher = ''.join([item[0] for item in cipher_counts.most_common()])

# Creating a mapping based on letter frequency
mapping = {}
for i, letter in enumerate(sorted_cipher):
    mapping[letter] = english_frequencies[i]
# Adjusting the mapping

mapping['z'] = 'H'
mapping['f'] = 'N'
mapping['q'] = 'A'
mapping['l'] = 'O'
mapping['y'] = 'G'
mapping['o'] = 'T'
mapping['d'] = 'V'
mapping['r'] = 'L'
mapping['s'] = 'I'
mapping['e'] = 'U'
mapping['x'] = 'C'
mapping['b'] = 'D'
mapping['j'] = 'R'
mapping['g'] = 'M'
mapping['a'] = 'X'
mapping['v'] = 'Y'



# Decrypting the text using the mapping
decrypted_text = ''.join([mapping.get(char, char) for char in cipher_text])
# Printing the adjusted mapping
for key, value in mapping.items():
    print(key,"=",value)
print(decrypted_text)