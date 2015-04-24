'''
Created on Mar 28, 2015

@author: Tuan Do
'''
def get_plural_form(singular_form):
    if singular_form[-2:] == 'sh' or\
     singular_form[-2:] == 'ss' or\
     singular_form[-2:] == 'ch' or\
     singular_form[-1:] == 'o' or\
     singular_form[-1:] == 'x':
        return singular_form + 'es'
    
    if singular_form[-2:] == 'fe':
        return singular_form[:-2] + 'ves'
    if singular_form[-1:] == 'f':
        return singular_form[:-1] + 'ves'
    if singular_form[-1:] == 'y' and\
     singular_form[-2] not in ['a', 'e', 'u', 'o', 'i']:
        return singular_form[:-1] + 'ies'
    return singular_form + 's'

if __name__ == '__main__':
    print get_plural_form('calf')
    print get_plural_form('knife')
    print get_plural_form('dog')
    print get_plural_form('watch')
    print get_plural_form('giraffe')