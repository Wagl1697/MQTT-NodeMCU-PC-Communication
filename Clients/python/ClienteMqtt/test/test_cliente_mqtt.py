# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8  2022

@author: Andres Venialgo
"""
#from cliente_mqtt import Cliente_mqtt
from cliente_mqtt import Cliente_mqtt
import unittest

class TestCliente( unittest.TestCase):
    def setUp(self):
        host = "localhost"
        port = 1883
        self.client = Cliente_mqtt(host, port)
        
    def test_conexion(self):
        value = self.client.conectar_broker()
        self.assertEqual(value, True)
        self.client.desconectar_broker()
        
    def tearDown(self):
        pass
    
if __name__ == "__main__":
    unittest.main()