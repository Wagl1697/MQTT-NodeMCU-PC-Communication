# -*- coding: utf-8 -*-

import json
from uuid import getnode as get_mac
"""
"""
def generar_topic():
    mac = get_mac()
    mac = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))
    pendiente = '{}/pendiente'.format(mac)
    lista_topicos = ['boot_up','on','ram/total','ram/used','ram/free']

    topic_normal = []
    topic_pendiente = []
    for i in range (0,len (lista_topicos)):
        dict_aux = {'topic': "{raiz}/{topic}".format(raiz= mac, topic = lista_topicos[i] ), 'payload': ''}
        dict_aux2 = {'topic': "{raiz}/{topic}".format(raiz= pendiente, topic = lista_topicos[i] ), 'payload': ''}
        topic_normal.append( dict_aux)
        topic_pendiente.append(dict_aux2)
    
    with open('topics.json', 'w') as file:
        json.dump(topic_normal, file, indent= 4)

    with open('topics_pendiente.json', 'w') as file:
        json.dump(topic_pendiente, file, indent= 4)

if __name__ == '__main__':
    generar_topic()